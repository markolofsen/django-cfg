"""Cache-key builders for ``run_single``.

A target's output is replayed from the cache only when every input that shapes it is unchanged. The sliced spec and
the tool options are hashed by ``cache.compute_target_cache_key``; this module supplies the rest:

* ``target_signature`` — target name, tool, groups, where the tree is published (stage folders normalized away: a
  stage has a fresh random name every run), **the generator's own code** and **the external tool's identity**.

  Without the generator code in the key, an edit to a post-processor with an unchanged spec replays stale output.
  The orchestrator used to delete every fingerprint at the start of each run for that reason, which meant no target
  was ever served from the cache.

* ``target_cache_slot`` — the on-disk slot name used by ``cache.restore_target_output`` / ``store_target_output``.
"""

from __future__ import annotations

import datetime
import functools
import hashlib
import importlib.metadata
import json
import re
import shutil
from pathlib import Path

from ..config import GenerationTarget

_GENERATOR_ROOT = Path(__file__).resolve().parents[3]  # modules/django_generator
_CONTRACT = _GENERATOR_ROOT.parents[1] / "core" / "contract.py"
_STAGE_PART = re.compile(r"^\.(?P<name>.+)\.djcfg-stage-[0-9a-f]+$")


def target_cache_slot(target: GenerationTarget, groups: list[str]) -> str:
    suffix = "+".join(sorted(groups)) or "_all"
    return f"{target.name}__{suffix}"


def unstaged(path: Path) -> Path:
    """``…/.name.djcfg-stage-1a2b3c4d/name/x`` → ``…/name/x``: the folder a staged path is published to."""
    parts = list(Path(path).parts)
    for i, part in enumerate(parts[:-1]):
        m = _STAGE_PART.match(part)
        if m and parts[i + 1] == m.group("name"):
            return Path(*parts[:i], *parts[i + 1:])
    return Path(path)


@functools.lru_cache(maxsize=1)
def generator_signature() -> str:
    """django-cfg's version and the content of every generator source file (tests excluded)."""
    from django_cfg.core.contract import CFG_VERSION

    h = hashlib.sha256(str(CFG_VERSION).encode())
    files = sorted(
        p for p in _GENERATOR_ROOT.rglob("*.py")
        if "__pycache__" not in p.parts and "tests" not in p.parts and ".archive" not in p.parts
    )
    for path in [*files, _CONTRACT]:
        if path.is_file():
            h.update(path.relative_to(_GENERATOR_ROOT.parents[1]).as_posix().encode())
            h.update(b"\x00")
            h.update(path.read_bytes())
    return h.hexdigest()


def _file_identity(path: str | Path | None) -> str:
    """Path, size and mtime of an installed binary: a reinstall or upgrade changes it."""
    if not path:
        return "missing"
    try:
        stat = Path(path).stat()
    except OSError:
        return f"{path}:missing"
    return f"{path}:{stat.st_size}:{int(stat.st_mtime)}"


def _tree_hash(root: Path, pattern: str) -> str:
    h = hashlib.sha256()
    for path in sorted(Path(root).rglob(pattern)):
        if path.is_file():
            h.update(path.relative_to(root).as_posix().encode())
            h.update(path.read_bytes())
    return h.hexdigest()


def tool_signature(target: GenerationTarget) -> str:
    """What the external tool contributes to the output besides the spec: its version, and its other inputs."""
    from ...tools.external import ogen, orval, progenitor

    tool = target.tool
    if tool == "ogen":
        return _file_identity(ogen.find_binary())
    if tool == "progenitor":
        from ...tools.openapi_processor.rust.tool import (
            find_workspace_root,
            rustfmt_inputs,
            rustfmt_version,
        )

        consumer = unstaged(target.path)
        # The crate is formatted last: the rustfmt binary, its config and the pinned toolchain shape every .rs file.
        identity = "|".join((
            _file_identity(progenitor.find_binary()),
            rustfmt_version(consumer),
            hashlib.sha256(rustfmt_inputs(consumer)).hexdigest(),
        ))
        if (target.options or {}).get("workspace"):
            # A member crate inherits the root's package keys: the root manifest shapes its Cargo.toml.
            root = find_workspace_root(consumer.parent)
            manifest = (root / "Cargo.toml").read_bytes() if root else b"none"
            identity += "|" + hashlib.sha256(manifest).hexdigest()
        return identity
    if tool == "swift-openapi":
        return _file_identity(shutil.which("swift-openapi-generator"))
    if tool == "openapi-python-client":
        try:
            return importlib.metadata.version("openapi-python-client")
        except importlib.metadata.PackageNotFoundError:
            # Run through `uvx`, which resolves the newest release: refresh at least daily.
            return f"uvx:{datetime.date.today().isoformat()}"
    if tool == "orval":
        from ..errors import GeneratorError
        from .dispatch import _find_frontend_workspace, runtime_import_for

        consumer = unstaged(target.path)
        try:
            workspace = _find_frontend_workspace(consumer)
        except GeneratorError:
            return "no-workspace"  # Orval itself fails on this target, with the reason
        prettier = hashlib.sha256()
        for folder in [consumer, *consumer.parents]:
            for config in sorted(folder.glob(".prettierrc*")) + sorted(folder.glob("prettier.config.*")):
                prettier.update(config.read_bytes())
            if folder == workspace:
                break
        return json.dumps(
            [orval.installed_version(workspace), orval.node_version(), repr(runtime_import_for(consumer)),
             prettier.hexdigest()],
        )
    if tool in ("buf", "grpc-python"):
        # The output is a function of the .proto files, not of the OpenAPI slice.
        proto_dir = (target.options or {}).get("proto_dir")
        proto = _tree_hash(Path(proto_dir), "*.proto") if proto_dir and Path(proto_dir).is_dir() else "none"
        binary = shutil.which("buf") if tool == "buf" else shutil.which("protoc")
        return f"{proto}|{_file_identity(binary)}"
    return tool


def target_signature(
    target: GenerationTarget,
    groups: list[str],
    out_dir: Path,
) -> str:
    return "|".join((
        target.name,
        target.tool,
        "+".join(sorted(groups)),
        unstaged(out_dir).as_posix(),
        unstaged(target.path).as_posix(),
        generator_signature(),
        tool_signature(target),
    ))


__all__ = ["generator_signature", "target_cache_slot", "target_signature", "tool_signature", "unstaged"]
