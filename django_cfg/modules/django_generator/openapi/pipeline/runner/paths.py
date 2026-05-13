"""Filesystem helpers used across the runner.

These functions only deal with paths and tree mirroring — no spec
loading, no tool dispatch, no cache. Kept tiny so the rest of the
runner can import them without dragging in the heavy modules.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from ..config import GenerationTarget, OpenAPIConfig
from ..fs import mirror_tree


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


def publish_to_consumer(target: GenerationTarget) -> None:
    """Copy the freshly generated tree from ``source_path`` to ``target.path``.

    No-op when ``source_path`` isn't set, when the two paths are the
    same, or when the source tree is empty. The destination is replaced
    wholesale — anything the consumer kept under that path (manual
    edits, stale files from a previous layout) is removed.
    """
    if target.source_path is None:
        return
    src = Path(target.source_path)
    dst = Path(target.path)
    if src.resolve() == dst.resolve():
        return
    if not src.exists():
        return
    try:
        if dst.exists():
            shutil.rmtree(dst)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, dst)
    except OSError:
        return


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
    "publish_to_consumer",
]
