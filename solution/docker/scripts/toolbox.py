"""One signed first-install toolbox build, shared by legacy and canonical launchers.

The private receipt is an operator-owned local attestation, not a registry
signature. It binds the build output ID, verified release bytes, recipe and
local daemon; it never authenticates an arbitrary preexisting image tag.
"""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import secrets
import stat
import subprocess
import tempfile

from cmdop_release import (PLATFORMS, digest, download_artifact, read_json,
                           require, verify_release)

IMAGE_ID = re.compile(r"sha256:[0-9a-f]{64}")
RECEIPT = "toolbox.json"
STABLE_URL = "https://install.cmdop.ai/releases/stable.json"


def docker(*args, timeout=30):
    proc = subprocess.run(["docker", *args], capture_output=True, text=True, timeout=timeout)
    require(proc.returncode == 0, "Docker command failed: " + " ".join(args[:2]))
    return proc.stdout.strip()


def daemon_identity():
    # Local binds must refer to this operator's filesystem, not a remote host.
    context = docker("context", "show")
    endpoint = docker("context", "inspect", context, "--format", "{{.Endpoints.docker.Host}}")
    if os.environ.get("DOCKER_HOST") and not os.environ.get("DOCKER_CONTEXT"):
        endpoint = os.environ["DOCKER_HOST"]
    require(endpoint.startswith("unix://"), "Canonical toolbox requires a local Unix Docker endpoint")
    info = json.loads(docker("info", "--format", "{{json .}}"))
    arch = {"x86_64": "amd64", "amd64": "amd64", "aarch64": "arm64", "arm64": "arm64"}.get(info.get("Architecture"))
    platform = info.get("OSType", "") + "/" + str(arch)
    require(platform in PLATFORMS and isinstance(info.get("ID"), str) and info["ID"],
            "Unsupported or unidentified Docker daemon")
    return {"id": info["ID"], "endpoint": endpoint, "platform": platform}


def stable_toolbox_recipe(source):
    before = "ARG MACHINE_IMAGE=docker-cfg-machine:local\nFROM ${MACHINE_IMAGE} AS machine"
    require(source.count(before) == 1, "Toolbox recipe changed; review the release donor stage")
    return source.replace(before, "FROM scratch AS machine\nCOPY --chmod=0755 cmdop /opt/cmdop/bin/cmdop", 1)


def recipe_sources(root):
    folder = Path(root) / "docker/toolbox"
    result = {}
    for name in ("Dockerfile", "tools.sh", "entry.sh"):
        p = folder / name
        require(p.is_file() and not p.is_symlink(), "Missing reviewed toolbox source: " + name)
        result[name] = p.read_bytes()
    return result


def recipe_inputs(root):
    files = recipe_sources(root)
    files["Dockerfile"] = stable_toolbox_recipe(files["Dockerfile"].decode()).encode()
    return files


def stable_toolbox_context(root, context, artifact):
    context = Path(context)
    context.mkdir(mode=0o700)
    sources = recipe_sources(root)
    files = {**sources, "Dockerfile": stable_toolbox_recipe(sources["Dockerfile"].decode()).encode()}
    for name, data in files.items():
        (context / name).write_bytes(data)
    download_artifact(context / "cmdop", artifact)
    return ({name: digest(data) for name, data in sources.items()},
            {**{name: digest(data) for name, data in files.items()}, "cmdop": artifact["sha256"]})


def fetch_stable():
    raw = subprocess.check_output(["curl", "-fsSL", "--proto", "=https",
                                   "--proto-redir", "=https", "--max-time", "30",
                                   "--max-filesize", "1048576", STABLE_URL], timeout=35)
    return raw, verify_release(raw, expected_version=None)


def image_metadata(image):
    require(isinstance(image, str) and IMAGE_ID.fullmatch(image), "Expected immutable toolbox image ID")
    values = json.loads(docker("image", "inspect", image))
    require(len(values) == 1 and values[0].get("Id") == image, "Toolbox image identity differs")
    item = values[0]
    return {"id": image, "platform": item["Os"] + "/" + item["Architecture"],
            "user": item["Config"].get("User"), "labels": item["Config"].get("Labels") or {}}


def private_directory(path):
    path = Path(path)
    require(path.is_dir() and not path.is_symlink() and path.resolve() == path.absolute(),
            "Toolbox receipt directory must be a real private path")
    info = path.stat()
    require(info.st_uid == os.getuid() and stat.S_IMODE(info.st_mode) == 0o700,
            "Toolbox receipt directory must be operator-owned mode 0700")
    return path


def write_receipt(directory, report):
    directory = private_directory(directory)
    dest = directory / RECEIPT
    require(not dest.exists() and not dest.is_symlink(), "Toolbox receipt already exists")
    fd, tmp = tempfile.mkstemp(prefix=".toolbox-", dir=directory)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w") as f:
            json.dump(report, f, indent=2)
            f.write("\n")
        # Atomic publication without overwriting a previous trusted receipt.
        os.link(tmp, dest)
    finally:
        os.unlink(tmp)
    return dest


def verified_image(root, directory, uid, gid, project):
    directory = private_directory(directory)
    path = directory / RECEIPT
    require(path.is_file() and not path.is_symlink(), "No verified toolbox receipt; run bootstrap")
    info = path.stat()
    require(info.st_uid == os.getuid() and stat.S_IMODE(info.st_mode) == 0o600
            and 0 < info.st_size <= 2 * 1024 * 1024, "Unsafe toolbox receipt")
    report = read_json(path.read_bytes())
    return validate_report(root, report, uid, gid, project)


def validate_report(root, report, uid, gid, project):
    require(isinstance(report, dict), "Invalid toolbox receipt")
    require(report.get("schema_version") == 1 and report.get("project") == project
            and report.get("uid") == uid and report.get("gid") == gid,
            "Toolbox receipt belongs to another installation")
    daemon = daemon_identity()
    require(report.get("daemon") == daemon, "Toolbox receipt Docker daemon/platform differs")
    built_at = datetime.fromisoformat(report["built_at"])
    require(built_at.tzinfo is not None and built_at <= datetime.now(timezone.utc),
            "Invalid toolbox build time")
    # The initial release was valid at installation. Existing deployments
    # use the native updater; expiration of the original envelope must not
    # prevent an ordinary restart of the already verified base image.
    release = verify_release(report["signed_envelope"].encode(), built_at, expected_version=None)
    artifact = release["artifacts"][daemon["platform"]]
    expected = {name: digest(data) for name, data in recipe_inputs(root).items()}
    expected["cmdop"] = artifact["sha256"]
    source_hashes = {name: digest(data) for name, data in recipe_sources(root).items()}
    require(report.get("release") == release and report.get("context_sha256") == expected
            and report.get("source_sha256") == source_hashes,
            "Toolbox signed artifact or recipe differs; review and rebuild explicitly")
    image_id = report["image_id"]
    require(isinstance(image_id, str) and IMAGE_ID.fullmatch(image_id)
            and image_id in report.get("build_digests", []), "Toolbox image ID differs from the build output")
    image = image_metadata(image_id)
    require(image["platform"] == daemon["platform"] and image["user"] == "developer"
            and image["labels"].get("com.docker-cfg.toolchain.build") == report["build_id"],
            "Toolbox image does not match the verified build")
    return image["id"]


def build_stable(root, directory, project, uid, gid, *, retain=True):
    """Build through the existing signed stable recipe; no app lifecycle or updater."""
    directory = private_directory(directory)
    require(re.fullmatch(r"[a-z][a-z0-9-]{2,40}", project), "Invalid toolbox project name")
    require(type(uid) is int and uid > 0 and type(gid) is int and gid > 0, "Expected non-root toolbox owner")
    if retain:
        require(not (directory / RECEIPT).exists() and not (directory / RECEIPT).is_symlink(),
                "Toolbox receipt already exists")
    daemon = daemon_identity()
    raw, release = fetch_stable()
    artifact = release["artifacts"][daemon["platform"]]
    build_id = secrets.token_hex(12)
    builder = "cfg-toolbox-" + build_id
    tag = project + "-toolbox:verified-" + build_id
    require(not docker("image", "ls", "-q", "--filter", "reference=" + tag),
            "Toolbox candidate tag collision")
    require(builder not in docker("buildx", "ls", "--format", "{{.Name}}").splitlines(),
            "Toolbox builder collision")
    created = False
    success = False
    try:
        with tempfile.TemporaryDirectory(prefix="toolbox-build-", dir=directory) as d:
            context = Path(d) / "context"
            source_hashes, hashes = stable_toolbox_context(root, context, artifact)
            print("Verified current stable CMDOP", release["version"], daemon["platform"], flush=True)
            docker("buildx", "create", "--name", builder, "--driver", "docker-container",
                   "--driver-opt", "memory=4g,cpu-quota=200000,cpu-period=100000")
            created = True
            iid = Path(d) / "image-id"
            meta = Path(d) / "metadata.json"
            subprocess.run(["docker", "buildx", "build", "--builder", builder,
                            "--platform", daemon["platform"], "--pull", "--load",
                            "--tag", tag, "--iidfile", str(iid), "--metadata-file", str(meta), "--progress", "plain",
                            "--label", "com.docker-cfg.toolchain.build=" + build_id,
                            "--build-arg", "LOCAL_UID=" + str(uid),
                            "--build-arg", "LOCAL_GID=" + str(gid), str(context)],
                           check=True, timeout=360)
            # Buildx iidfile can contain a manifest digest with the container
            # image store. Resolve the unique build-owned tag to its config ID
            # and use only that immutable ID for execution and the receipt.
            image_id = docker("image", "inspect", tag, "--format", "{{.Id}}")
            build_metadata = read_json(meta.read_bytes())
            digests = sorted({value for value in (iid.read_text().strip(),
                        build_metadata.get("containerimage.digest"),
                        build_metadata.get("containerimage.config.digest"))
                        if isinstance(value, str) and IMAGE_ID.fullmatch(value)})
            require(image_id in digests, "Loaded toolbox differs from build output digest")
            image = image_metadata(image_id)
            require(image["platform"] == daemon["platform"] and image["user"] == "developer"
                    and image["labels"].get("com.docker-cfg.toolchain.build") == build_id,
                    "Unexpected built toolbox image")
            output = docker("run", "--rm", "--pull", "never", "--network", "none",
                            "--read-only", "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
                            "--cpus", "1", "--memory", "512m", "--pids-limit", "64",
                            "--entrypoint", "/bin/sh", image_id, "-ec",
                            "test \"$(id -u)\" = " + str(uid) + "; test \"$(id -g)\" = " + str(gid) +
                            "; exec /usr/local/bin/docker-cfg-tools --report", timeout=45)
            versions = [x.split() for x in output.splitlines() if x.startswith("cmdop ")]
            require(len(versions) == 1 and len(versions[0]) >= 2 and versions[0][1] == release["version"]
                    and any(x.split() == [artifact["sha256"], "/usr/local/bin/cmdop"]
                            for x in output.splitlines()), "Built toolbox binary differs from signed release")
            require(daemon_identity() == daemon, "Docker daemon changed during toolbox build")
            report = {"schema_version": 1, "project": project, "uid": uid, "gid": gid,
                      "daemon": daemon, "built_at": datetime.now(timezone.utc).isoformat(),
                      "signed_envelope": raw.decode(), "release": release,
                      "source_sha256": source_hashes, "context_sha256": hashes,
                      "build_digests": digests, "build_id": build_id,
                      "image_id": image_id, "image_tag": tag}
            require(validate_report(root, report, uid, gid, project) == image_id,
                    "Toolbox receipt verification failed")
            if retain:
                write_receipt(directory, report)
            success = True
            print(output, flush=True)
            return report
    finally:
        if created:
            docker("buildx", "rm", builder, timeout=60)
        if not success and docker("image", "ls", "-q", "--filter", "reference=" + tag):
            owner = docker("image", "inspect", tag, "--format",
                           '{{index .Config.Labels "com.docker-cfg.toolchain.build"}}')
            require(owner == build_id, "Refusing cleanup of foreign toolbox image")
            docker("image", "rm", tag)
