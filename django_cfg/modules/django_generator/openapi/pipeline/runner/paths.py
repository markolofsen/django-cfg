"""Filesystem helpers used across the runner.

These functions only deal with paths and tree mirroring — no spec
loading, no tool dispatch, no cache. Kept tiny so the rest of the
runner can import them without dragging in the heavy modules.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from ..config import GenerationTarget, OpenAPIConfig
from ..errors import WriteError
from ..fs import mirror_tree
from ..staging import Stage


def cache_dir(config: OpenAPIConfig) -> Path:
    """Project-local ``openapi/.cache/`` directory.

    Lives under the same root the OpenAPI output goes to so it's easy
    to nuke (``rm -rf openapi/.cache``) without affecting source code.

    .. note::

        If you add new endpoints or change ``@extend_schema`` tags and
        ``make gen`` does not reflect them, the global spec cache is likely
        stale.  Delete ``openapi/.cache/`` and re-run::

            rm -rf openapi/.cache && make gen

        The spec cache key is based on the Django project fingerprint, not
        on individual view changes, so tag edits can be invisible to the
        cache invalidator.
    """
    return config.get_output_path() / ".cache"


def effective_root(target: GenerationTarget) -> Path:
    """Where the pipeline actually writes for this target.

    With ``source_path`` set, generation lands in the Django project
    under ``<source_root>/<target.name>/``. Without it, falls back to
    ``target.path`` (legacy behavior — generation writes straight into
    the consumer dir).
    """
    return Path(target.source_path) if target.source_path is not None else Path(target.path)


def find_project_root(start: Path) -> Path:
    """Walk up from ``start`` looking for a ``.git`` or ``Makefile``
    marker; fall back to ``start.parent`` if neither is found."""
    cur = start.resolve()
    for parent in [cur, *cur.parents]:
        if (parent / ".git").exists() or (parent / "Makefile").exists():
            return parent
    return start.parent


def stage_consumer(target: GenerationTarget, built: Path) -> Stage | None:
    """Stage the copy of a freshly generated tree for the consumer ``target.path``.

    ``None`` when ``source_path`` isn't set or both paths are the same folder
    (nothing to publish). Otherwise returns a ``Stage`` next to ``target.path``
    holding a copy of ``built`` (the staged source tree); the caller checks and
    commits it. The consumer folder is replaced wholesale on commit, as before;
    until then it is untouched.
    """
    if target.source_path is None:
        return None
    if Path(target.source_path).resolve() == Path(target.path).resolve():
        return None
    stage = Stage.open(Path(target.path), seed=False)
    try:
        shutil.copytree(built, stage.path, symlinks=True, dirs_exist_ok=True)
    except OSError as e:
        stage.discard()
        raise WriteError(f"cannot stage the copy for {target.path}: {e}") from e
    return stage


def mirror_target_to_tmp(target: GenerationTarget) -> None:
    """Copy a target's output under ``<project>/.tmp/generated/<name>/``.

    No-op when ``source_path`` is set — that path *is* the source of
    truth, so a tmp mirror would be redundant. Used when ``mirror_to_tmp``
    is enabled in config.
    """
    if target.source_path is not None:
        return
    out = Path(target.path)
    if not out.exists():
        return
    root = find_project_root(out)
    mirror_tree(out, root / ".tmp" / "generated", target.name)


__all__ = [
    "cache_dir",
    "effective_root",
    "find_project_root",
    "mirror_target_to_tmp",
    "stage_consumer",
]
