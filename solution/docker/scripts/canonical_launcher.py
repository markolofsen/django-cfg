"""Guarded host-side launcher for the one canonical Django CFG customer Git root.

Secrets stay outside the checkout. No implicit Docker up, public preview,
machine admission, production migration or host-wide cleanup.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import secrets
import stat
import subprocess
import sys
from urllib.parse import urlsplit, urlunsplit

from isolation import assert_ports_free, claim_project
from toolbox import RECEIPT, build_stable, private_directory, verified_image

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = ROOT / "docker/canonical/compose.yaml"
PROJECT_NAME = re.compile(r"^[a-z][a-z0-9-]{2,40}$")
MACHINE_NAME = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,63}$")
IDENTIFIER = re.compile(r"^[A-Z][A-Z0-9_]*$")
PORTS = ("DEMO_PORT", "DOCS_PORT", "STORYBOOK_PORT", "API_PORT")
OPTIONAL = {"POSTGRES_DB", "POSTGRES_USER", "SITE_URL", "API_URL",
            "CMDOP_SERVER", "CMDOP_ACCEPT_AGREEMENT"}
REQUIRED = (
    "COMPOSE_PROJECT_NAME", "CANONICAL_CUSTOMER_ROOT", "CANONICAL_PROJECTS_DIR",
    "CANONICAL_RUNTIME_DIR", "DJANGO_SECRET_KEY",
    "DATABASE_URL", "POSTGRES_PASSWORD", "CMDOP_MACHINE_NAME",
    "LOCAL_UID", "LOCAL_GID", *PORTS,
)
EXPECTED_SERVICES = {
    "deps", "frontend-deps", "db", "redis", "migrate", "api",
    "demo", "docs", "storybook", "gateway", "workspace",
}
MOUNTPOINTS = ("django/media", "django/staticfiles",
               "frontend/apps/demo/.next", "frontend/apps/docs/.next")


VOLUME_KEYS = {"python-deps", "dependency-cache", "database", "django-data",
               "django-static", "django-media", "machine-home"}
NETWORK_INTERNAL = {"dev": True, "egress": False}
BACKEND_MOUNTS = {
    ("python-deps", "/opt/venv", True),
    ("django-data", "/var/dev-data", False),
    ("django-static", "/workspace/solution/projects/django/staticfiles", False),
    ("django-media", "/workspace/solution/projects/django/media", False),
}
NAMED_MOUNTS = {
    "api": BACKEND_MOUNTS, "migrate": BACKEND_MOUNTS,
    "db": {("database", "/var/lib/postgresql/data", False)},
    "deps": {("python-deps", "/opt/venv", False),
             ("dependency-cache", "/var/dev-data", False)},
    "frontend-deps": {("dependency-cache", "/var/dev-data", False)},
    **{name: {("dependency-cache", "/var/dev-data", True)}
       for name in ("demo", "docs", "storybook")},
    "workspace": {("machine-home", "/home/developer", False)},
}


def validate_resource_definitions(model: dict, project: str, machine: bool) -> None:
    volumes = model.get("volumes", {})
    expected = VOLUME_KEYS if machine else VOLUME_KEYS - {"machine-home"}
    require(set(volumes) == expected, "Unexpected canonical volume keys")
    for key, volume in volumes.items():
        require(volume.get("name") == project + "_" + key
                and volume.get("driver", "local") == "local"
                and not volume.get("external", False)
                and not set(volume) - {"name", "driver", "external"},
                "Unsafe canonical volume definition: " + key)
    networks = model.get("networks", {})
    require(set(networks) == set(NETWORK_INTERNAL), "Unexpected canonical network keys")
    for key, network in networks.items():
        require(network.get("name") == project + "_" + key
                and network.get("driver", "bridge") == "bridge"
                and not network.get("external", False)
                and network.get("internal", False) == NETWORK_INTERNAL[key]
                and not network.get("ipam")
                and not set(network) - {"name", "driver", "external", "internal", "ipam"},
                "Unsafe canonical network definition: " + key)


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def real_dir(value: str | Path, label: str) -> Path:
    path = Path(value).expanduser()
    require(path.is_absolute() and not path.is_symlink()
            and path.is_dir(), "Expected non-symlink directory: " + label)
    return path.resolve()


def customer_root(value: str | Path) -> Path:
    root = real_dir(value, "customer Git root")
    try:
        actual = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            text=True, stderr=subprocess.DEVNULL, timeout=15).strip()
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError("Expected an independent customer Git repository") from exc
    require(Path(actual).resolve() == root, "Customer root is nested in another Git checkout")
    require((root / ".git").exists(), "Customer Git metadata missing")
    return root


def verify_source(env: dict[str, str], *, machine: bool = False) -> tuple[Path, Path]:
    root = customer_root(env["CANONICAL_CUSTOMER_ROOT"])
    source = real_dir(env["CANONICAL_PROJECTS_DIR"], "canonical projects directory")
    require(source == root / "solution/projects", "Projects must be at this customer's Git root")
    for part in ("django", "frontend"):
        folder = source / part
        require(folder.is_dir() and not folder.is_symlink(), "Missing canonical " + part)
    for name in ("django/manage.py", "django/uv.lock", "frontend/package.json",
                 "frontend/pnpm-lock.yaml", "frontend/apps/demo/package.json",
                 "frontend/apps/docs/package.json", "frontend/apps/storybook/package.json"):
        path = source / name
        require(path.is_file() and not path.is_symlink(),
                "Missing canonical source input: " + name)
    runtime = real_dir(env["CANONICAL_RUNTIME_DIR"], "reviewed runtime source")
    for filename in ("frontend-deps.sh", "nginx.conf", "workspace.py"):
        f = runtime / filename
        require(f.is_file() and not f.is_symlink(),
                "Missing reviewed runtime source: " + filename)
    if machine:
        # The CMDOP worker may edit this Git checkout but must never inherit
        # the operator's private configuration or another machine identity.
        for name in (".env", ".secrets", ".ssh", ".aws", "machine-home",
                     "runtime/machine-home", "runtime/agent.env"):
            candidate = root / name
            require(not candidate.exists() and not candidate.is_symlink(),
                    "Customer Git checkout contains a private machine secret path: " + name)
        for path in root.rglob(".env"):
            if any(x in {".git", "node_modules", ".next"} for x in path.relative_to(root).parts):
                continue
            raise ValueError("Customer Git checkout has a private .env not safe for CMDOP workspace")
    return root, source


def load_env(envfile: Path) -> dict[str, str]:
    require(envfile.is_file() and not envfile.is_symlink(), "Private environment is missing")
    info = envfile.stat()
    require(info.st_uid == os.getuid() and (stat.S_IMODE(info.st_mode) & 0o077) == 0,
            "Private environment must be owned by the operator and mode 0600")
    values: dict[str, str] = {}
    for line in envfile.read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        key, sep, val = line.partition("=")
        require(sep == "=" and IDENTIFIER.fullmatch(key) and key not in values
                and not any(ord(c) < 32 for c in val),
                "Invalid or duplicate private environment field")
        values[key] = val
    require(set(values) <= set(REQUIRED) | OPTIONAL, "Unexpected canonical environment field")
    require(all(values.get(key) for key in REQUIRED), "Missing canonical environment field")
    require(bool(PROJECT_NAME.fullmatch(values["COMPOSE_PROJECT_NAME"])),
            "Invalid canonical Compose project name")
    require(bool(MACHINE_NAME.fullmatch(values["CMDOP_MACHINE_NAME"])),
            "Invalid CMDOP machine name")
    require(values["LOCAL_UID"] == str(os.getuid()) and values["LOCAL_GID"] == str(os.getgid()),
            "Canonical runtime UID/GID differs from current checkout owner")
    ports = [int(values[k]) if values[k].isdigit() else -1 for k in PORTS]
    require(len(set(ports)) == 4 and all(1024 <= n <= 65535 for n in ports),
            "Require four distinct unprivileged loopback ports")
    db = urlsplit(values["DATABASE_URL"])
    require(db.scheme in ("postgres", "postgresql") and db.hostname == "db"
            and db.username == "docker_cfg" and db.port == 5432,
            "Database URL must use the isolated Docker database")
    root, _ = verify_source(values)
    require(not envfile.resolve().is_relative_to(root),
            "Secrets must be outside the agent-accessible customer checkout")
    private_directory(envfile.parent)
    return values


def selected_image(envfile: Path, env: dict) -> str:
    return verified_image(ROOT, envfile.parent, int(env["LOCAL_UID"]),
                          int(env["LOCAL_GID"]), env["COMPOSE_PROJECT_NAME"])


def _compose_raw(envfile: Path, values: dict, image: str, args: list[str],
                 *, capture: bool = False) -> subprocess.CompletedProcess:
    # Both the verified image and authoritative private configuration override
    # inherited interpolation values. No user-controlled image tag is passed.
    environ = {k: v for k, v in os.environ.items()
               if not k.startswith("COMPOSE_")}
    environ.update({key: "" for key in OPTIONAL})
    environ.update(values)
    environ["CANONICAL_TOOLBOX_IMAGE"] = image
    return subprocess.run(["docker", "compose", "--project-directory",
                           values["CANONICAL_CUSTOMER_ROOT"], "--env-file", str(envfile),
                           "-p", values["COMPOSE_PROJECT_NAME"],
                           "-f", str(COMPOSE), *args],
                          env=environ, text=True, capture_output=capture,
                          timeout=600, check=True)


def compose(envfile: Path, args: list[str], *, capture: bool = False) -> subprocess.CompletedProcess:
    values = load_env(envfile)
    image = selected_image(envfile, values)
    machine = "machine" in args
    # Validate the actual immutable image mapping and resource contract
    # before each lifecycle call, rather than trusting a previous prepare.
    _effective_config(envfile, values, image, machine=machine, stopping="stop" in args or "down" in args)
    return _compose_raw(envfile, values, image, args, capture=capture)


def effective_config(envfile: Path, *, machine: bool = False) -> dict:
    env = load_env(envfile)
    return _effective_config(envfile, env, selected_image(envfile, env), machine=machine)


def _effective_config(envfile: Path, env: dict, image: str, *, machine: bool = False, stopping: bool = False) -> dict:
    verify_source(env, machine=machine and not stopping)
    profiles = ["--profile", "tools"] + (["--profile", "machine"] if machine else [])
    result = _compose_raw(envfile, env, image, [*profiles, "config", "--format", "json"], capture=True)
    model = json.loads(result.stdout)
    require(model["name"] == env["COMPOSE_PROJECT_NAME"], "Compose project name changed")
    validate_resource_definitions(model, env["COMPOSE_PROJECT_NAME"], machine)
    services = model["services"]
    active = EXPECTED_SERVICES if machine else EXPECTED_SERVICES - {"workspace"}
    require(set(services) == active, "Unexpected canonical Compose service topology")
    ports = set()
    expected_port_values = {int(env[k]) for k in PORTS}
    third_party = {"db": "postgres:17-alpine", "redis": "redis:7.4-alpine",
                   "gateway": "nginx:1.28-alpine"}
    for name, service in services.items():
        require(service.get("image") == third_party.get(name, image)
                and service.get("pull_policy") == "never" and "build" not in service,
                "Unexpected canonical image selection: " + name)
        require(service.get("cap_drop") == ["ALL"]
                and (service.get("read_only") is True or
                     (name == "workspace" and not service.get("read_only", False)))
                and not service.get("privileged", False)
                and service.get("network_mode") != "host"
                and service.get("pid") != "host", "Unsafe canonical service: " + name)
        for binding in service.get("ports", []):
            require(name == "gateway" and binding["host_ip"] == "127.0.0.1",
                    "Non-loopback or foreign service port")
            ports.add(int(binding["published"]))
        named = []
        for mount in service.get("volumes", []):
            if mount["type"] == "volume":
                require(not mount.get("volume")
                        and not set(mount) - {"type", "source", "target", "read_only", "volume"},
                        "Unsafe canonical volume mount options: " + name)
                named.append((mount["source"], mount["target"], mount.get("read_only", False)))
                continue
            require(mount["type"] == "bind", "Unexpected canonical mount type: " + name)
            require(mount["bind"]["create_host_path"] is False,
                    "Auto-created host bind directory refused: " + name)
            resolved = Path(mount["source"]).resolve()
            _, source = verify_source(env)
            runtime = Path(env["CANONICAL_RUNTIME_DIR"]).resolve()
            root = Path(env["CANONICAL_CUSTOMER_ROOT"]).resolve()
            require(resolved in (source / "django", source / "frontend", root)
                    or (resolved.parent == runtime and resolved.name in
                        {"nginx.conf", "frontend-deps.sh", "workspace.py"}),
                    "Unexpected host bind: " + name)
            if resolved == root:
                require(name == "workspace" and not mount.get("read_only"),
                        "Only the explicit machine profile may write customer Git root")
            if resolved == source / "django":
                require(mount["read_only"], "Canonical Django source must be read-only")
        require(len(named) == len(set(named))
                and set(named) == NAMED_MOUNTS.get(name, set()),
                "Unexpected canonical named mounts: " + name)
        allowed_networks = {
            "deps": {"egress"}, "frontend-deps": {"egress"},
            "gateway": {"dev", "egress"}, "workspace": {"dev", "egress"},
        }
        require(set(service.get("networks", {}))
                == allowed_networks.get(name, {"dev"}),
                "Unexpected canonical network boundary: " + name)
        require(all(value in (None, {}) for value in service.get("networks", {}).values()),
                "Unexpected canonical network attachment options: " + name)
    require(ports == expected_port_values, "Canonical gateway port contract changed")
    require(model["networks"]["dev"]["internal"], "Canonical service network must be internal")
    return model


def prepare_source(env: dict, *, machine: bool = False) -> dict:
    root, source = verify_source(env, machine=machine)
    # The per-checkout owner receipt protects named Docker resources from
    # takeover by an unrelated clone. No source file or secret is replaced.
    claim_project(root, env["COMPOSE_PROJECT_NAME"], "canonical",
                  volume_keys=VOLUME_KEYS, network_internal=NETWORK_INTERNAL)
    for rel in MOUNTPOINTS:
        path = source / rel
        require(not path.is_symlink(), "Symlinked canonical mount target: " + rel)
        if path.exists():
            require(path.is_dir(), "Canonical mount target is not a directory: " + rel)
        else:
            path.mkdir(parents=True, mode=0o700)
    return {"project": env["COMPOSE_PROJECT_NAME"],
            "created_targets": list(MOUNTPOINTS), "machine_profile": machine}


def prepare(envfile: Path, *, machine: bool = False) -> dict:
    env = load_env(envfile)
    effective_config(envfile, machine=machine)
    return prepare_source(env, machine=machine)


def provision(envfile: Path, env: dict) -> str:
    prepare_source(env)
    receipt = envfile.parent / RECEIPT
    if not receipt.exists() and not receipt.is_symlink():
        build_stable(ROOT, envfile.parent, env["COMPOSE_PROJECT_NAME"],
                     int(env["LOCAL_UID"]), int(env["LOCAL_GID"]))
    # Never silently repair, replace or rebuild a mismatched receipt.
    return selected_image(envfile, env)


def init(root: Path, state: Path, runtime: Path, *, project: str,
         port: int, machine: str) -> Path:
    root = customer_root(root)
    source = root / "solution/projects"
    require(source.is_dir() and not source.is_symlink(), "Missing customer projects tree")
    runtime = real_dir(runtime, "canonical runtime directory")
    require(bool(PROJECT_NAME.fullmatch(project)) and bool(MACHINE_NAME.fullmatch(machine)),
            "Invalid project or machine name")
    require(1024 <= port <= 65532, "Four adjacent unprivileged ports are required")
    require(not state.exists() and not state.is_symlink(), "Private state directory already exists")
    state = state.absolute()
    require(state.resolve() == state, "Private state path must not traverse symlinks")
    require(not state.is_relative_to(root), "Private state must be outside the Git checkout")
    assert_ports_free([port + i for i in range(4)])
    state.mkdir(mode=0o700, parents=True)
    password = secrets.token_hex(24)
    values = {
        "COMPOSE_PROJECT_NAME": project,
        "CANONICAL_CUSTOMER_ROOT": str(root),
        "CANONICAL_PROJECTS_DIR": str(source),
        "CANONICAL_RUNTIME_DIR": str(runtime),
        "LOCAL_UID": str(os.getuid()), "LOCAL_GID": str(os.getgid()),
        "DJANGO_SECRET_KEY": secrets.token_urlsafe(48),
        "POSTGRES_PASSWORD": password, "POSTGRES_DB": "docker_cfg_dev",
        "POSTGRES_USER": "docker_cfg",
        "DATABASE_URL": urlunsplit(("postgresql", f"docker_cfg:{password}@db:5432",
                                    "/docker_cfg_dev", "", "")),
        "CMDOP_MACHINE_NAME": machine, "CMDOP_SERVER": "",
        "CMDOP_ACCEPT_AGREEMENT": "",
        "DEMO_PORT": str(port), "DOCS_PORT": str(port + 1),
        "STORYBOOK_PORT": str(port + 2), "API_PORT": str(port + 3),
        "SITE_URL": "http://localhost:" + str(port),
        "API_URL": "http://localhost:" + str(port + 3),
    }
    dest = state / "private.env"
    fd = os.open(dest, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "w") as f:
        for name, value in values.items():
            f.write(name + "=" + value + "\n")
    try:
        prepare_source(load_env(dest))
    except BaseException:
        dest.unlink(missing_ok=True)
        # Preserve the owned private directory for inspection; no Docker services launched.
        raise
    return dest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Canonical Django CFG runtime; no implicit start")
    commands = parser.add_subparsers(dest="action", required=True)
    first = commands.add_parser("init", help="Create isolated private config; do not start services")
    first.add_argument("--root", required=True, type=Path)
    first.add_argument("--state-dir", required=True, type=Path)
    first.add_argument("--runtime-dir", type=Path, default=ROOT / "docker/canonical")
    first.add_argument("--project", required=True)
    first.add_argument("--base-port", type=int, required=True)
    first.add_argument("--machine", required=True)
    for name in ("inspect", "prepare", "bootstrap", "start", "machine-start", "status", "stop"):
        opt = commands.add_parser(name)
        opt.add_argument("--env-file", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.action == "init":
            path = init(args.root, args.state_dir, args.runtime_dir,
                        project=args.project, port=args.base_port,
                        machine=args.machine)
            print(json.dumps({"state": "initialized_not_running", "private_env": str(path)}))
            return 0
        envfile = args.env_file.absolute()
        state = load_env(envfile)
        if args.action == "inspect":
            model = effective_config(envfile)
            print(json.dumps({"project": model["name"], "services": sorted(model["services"]),
                              "ports": [int(state[k]) for k in PORTS], "state": "config_only"}))
        elif args.action == "prepare":
            print(json.dumps(prepare(envfile)))
        elif args.action == "bootstrap":
            provision(envfile, state)
            prepare(envfile)
            for name in ("deps", "frontend-deps"):
                compose(envfile, ["--profile", "tools", "run", "-T", "--rm", "--no-deps", name])
            print(json.dumps({"state": "installed_not_running", "project": state["COMPOSE_PROJECT_NAME"]}))
        elif args.action == "start":
            prepare(envfile)
            compose(envfile, ["up", "-d", "--no-build", "db", "redis"])
            compose(envfile, ["--profile", "tools", "run", "-T", "--rm", "migrate"])
            compose(envfile, ["up", "-d", "--no-build", "api", "demo", "docs", "storybook", "gateway"])
            print(json.dumps({"state": "started_not_admitted", "project": state["COMPOSE_PROJECT_NAME"]}))
        elif args.action == "machine-start":
            prepare(envfile, machine=True)
            compose(envfile, ["--profile", "machine", "up", "-d", "--no-build", "--no-deps", "workspace"])
            print(json.dumps({"state": "awaiting_owner_admission", "project": state["COMPOSE_PROJECT_NAME"]}))
        elif args.action == "status":
            effective_config(envfile)
            compose(envfile, ["ps"])
        elif args.action == "stop":
            effective_config(envfile)
            root = customer_root(state["CANONICAL_CUSTOMER_ROOT"])
            claim_project(root, state["COMPOSE_PROJECT_NAME"], "canonical",
                          volume_keys=VOLUME_KEYS, network_internal=NETWORK_INTERNAL)
            compose(envfile, ["--profile", "machine", "stop"])
            print(json.dumps({"state": "stopped_volumes_retained", "project": state["COMPOSE_PROJECT_NAME"]}))
        return 0
    except (ValueError, OSError, subprocess.SubprocessError, KeyError, TypeError) as exc:
        # Never print parsed environment, passwords or command arguments.
        print("Canonical runtime refused: " + str(exc).splitlines()[0][:180], file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
