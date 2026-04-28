"""Filesystem helpers: atomic replace, mirror to .tmp/, hash tree."""

from __future__ import annotations

import hashlib
import os
import shutil
from pathlib import Path

from .errors import WriteError


def atomic_replace(src: Path, dst: Path) -> None:
    """Replace `dst` with `src` atomically.

    `src` and `dst` must live on the same filesystem (we use rename). Falls
    back to copy-then-rename for cross-fs scenarios.
    """
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_suffix(dst.suffix + ".swap")
    try:
        if dst.exists():
            os.replace(dst, tmp)
        os.replace(src, dst)
        if tmp.exists():
            if tmp.is_dir():
                shutil.rmtree(tmp)
            else:
                tmp.unlink()
    except OSError as e:
        raise WriteError(f"atomic_replace {src} → {dst}: {e}") from e


def mirror_tree(src: Path, mirror_root: Path, name: str) -> None:
    """Copy `src` → `mirror_root / name`, replacing if it exists.

    Used for the `.tmp/generated/<name>/` mirror; lets a developer eyeball
    every generated tree from one place.
    """
    if not src.exists():
        return
    dst = mirror_root / name
    try:
        if dst.exists():
            shutil.rmtree(dst)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, dst)
    except OSError as e:
        raise WriteError(f"mirror {src} → {dst}: {e}") from e


def hash_tree(root: Path) -> str:
    """Deterministic sha256 over file paths + contents under `root`."""
    h = hashlib.sha256()
    if not root.exists():
        return h.hexdigest()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix().encode()
        h.update(rel)
        h.update(b"\0")
        h.update(path.read_bytes())
        h.update(b"\0")
    return h.hexdigest()


__all__ = ["atomic_replace", "mirror_tree", "hash_tree"]
