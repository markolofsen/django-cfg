"""Fail closed before sharing Docker Compose names with an unrelated checkout.

The marker lives only in the ignored runtime of this checkout. Docker labels
prevent collisions with running containers, and an absent marker prevents
adopting orphaned named volumes/networks/images from another installation.
"""
import json
import os
import re
from pathlib import Path
import socket
import subprocess


def _docker(*args):
    result = subprocess.run(["docker", *args], capture_output=True, text=True, timeout=15)
    if result.returncode != 0:
        raise SystemExit("Docker ownership preflight failed; no lifecycle change attempted")
    return result.stdout


def assert_ports_free(ports):
    """Best-effort loopback collision preflight. Compose bind is authoritative."""
    for port in ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
                server.bind(("127.0.0.1", int(port)))
        except OSError:
            raise SystemExit(f"Loopback port {port} is already occupied; choose another --base-port")


def verify_project_resources(project, volume_keys, network_internal):
    """Reject exact-name collisions, including resources without Compose labels."""
    volumes = set(_docker("volume", "ls", "--format", "{{.Name}}").splitlines())
    for key in sorted(volume_keys):
        name = project + "_" + key
        if name not in volumes:
            continue
        items = json.loads(_docker("volume", "inspect", name))
        item = items[0] if len(items) == 1 else {}
        labels = item.get("Labels") or {}
        if (item.get("Name") != name or item.get("Driver") != "local"
                or item.get("Scope") != "local" or item.get("Options")
                or labels.get("com.docker.compose.project") != project
                or labels.get("com.docker.compose.volume") != key):
            raise SystemExit("Unowned or unsafe canonical Docker volume: " + name)
    networks = [line.split(maxsplit=1) for line in
                _docker("network", "ls", "--no-trunc", "--format", "{{.ID}} {{.Name}}").splitlines()]
    for key, internal in sorted(network_internal.items()):
        name = project + "_" + key
        ids = [parts[0] for parts in networks if len(parts) == 2 and parts[1] == name]
        if not ids:
            continue
        if len(ids) != 1:
            raise SystemExit("Ambiguous canonical Docker network: " + name)
        items = json.loads(_docker("network", "inspect", ids[0]))
        item = items[0] if len(items) == 1 else {}
        labels = item.get("Labels") or {}
        if (item.get("Name") != name or item.get("Driver") != "bridge"
                or item.get("Scope") != "local" or item.get("Internal") is not internal
                or item.get("Options")
                or labels.get("com.docker.compose.project") != project
                or labels.get("com.docker.compose.network") != key):
            raise SystemExit("Unowned or unsafe canonical Docker network: " + name)


def claim_project(root, project, image_revision="dev-v1", *,
                  volume_keys=(), network_internal=None):
    """Accept only a fresh project or the same owned checkout, never another one."""
    if not re.fullmatch(r"[a-z][a-z0-9-]{2,40}", project):
        raise SystemExit("Invalid Compose project name")
    root = Path(root).resolve()
    receipt = root / "runtime" / "project-owner.json"
    expected = {"project": project, "checkout": str(root)}
    if receipt.exists() or receipt.is_symlink():
        if receipt.is_symlink():
            raise SystemExit("Project ownership receipt must be a regular file")
        try:
            found = json.loads(receipt.read_text())
        except (OSError, ValueError):
            raise SystemExit("Invalid project ownership receipt; refusing Docker operations")
        if found != expected:
            raise SystemExit("Project ownership receipt belongs to another installation")
        has_claim = True
    else:
        has_claim = False

    ids = _docker("ps", "-aq", "--filter", "label=com.docker.compose.project=" + project).split()
    containers = json.loads(_docker("inspect", *ids)) if ids else []
    owner_paths = {
        str(item.get("Config", {}).get("Labels", {}).get("com.docker.compose.project.working_dir") or "")
        for item in containers
    }
    if owner_paths and owner_paths != {str(root)}:
        raise SystemExit("Compose project name is already owned by a different checkout; use ./dev init --project UNIQUE")
    own_running_or_stopped = bool(containers)

    if not has_claim and not own_running_or_stopped:
        # Docker volumes/networks survive 'compose down' without -v. They can
        # contain an unknown owner's DB and independent CMDOP identity.
        for args in (
            ("volume", "ls", "-q", "--filter", "label=com.docker.compose.project=" + project),
            ("network", "ls", "-q", "--filter", "label=com.docker.compose.project=" + project),
        ):
            if _docker(*args).strip():
                raise SystemExit("Project name has existing Docker volumes/networks without an ownership receipt")
        for reference in (f"{project}-toolbox:*", f"{project}-machine:*"):
            if _docker("image", "ls", "-q", "--filter", "reference=" + reference).strip():
                raise SystemExit("Project name has a preexisting image tag without an ownership receipt")

    if volume_keys or network_internal:
        verify_project_resources(project, volume_keys, network_internal or {})

    if not has_claim:
        receipt.parent.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(receipt, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            if json.loads(receipt.read_text()) != expected:
                raise SystemExit("Concurrent project-ownership claim conflicts")
        else:
            with os.fdopen(fd, "w") as file:
                json.dump(expected, file, indent=2)
                file.write("\n")
    return expected
