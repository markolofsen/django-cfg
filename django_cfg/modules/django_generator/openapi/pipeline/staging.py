"""Staged output: generate next to the real folder, replace it only on success.

Every generator in this package cleans its output folder before it writes
(``rmtree(out_dir)``, ``Cleaned N items``). Done in place, a failure halfway
leaves the folder empty or half written, and whatever was in it is gone. On
2026-11-18 the ORM target of carapis emptied ``_shared/orm`` and then failed
on an app that no longer existed; seven uncommitted files went with it.

So a generator never writes to its output folder directly:

1. ``Stage.open(dst)`` copies ``dst`` to ``<parent>/.<name>.djcfg-stage-<id>/<name>``
   (same filesystem, same leaf name, so a tool that derives a package name from
   the folder sees the same name). The generator cleans and writes there, so it
   starts from exactly what it found before and the result is the same as an
   in-place run.
2. On failure, ``discard()`` deletes the staging folder. ``dst`` was never touched.
3. On success, ``commit(force=...)`` first checks git (below), then swaps:
   ``dst`` -> ``.<name>.djcfg-old-<id>``, staging -> ``dst``, old deleted. If the
   second rename fails the first is undone.

The guard. If ``dst`` is inside a git work tree and ``git status`` lists
uncommitted changes under it, each changed file is checked: it is the
generator's own if its content equals what the generator wrote last time
(a manifest kept in ``.git/django-cfg-gen/``, never in the work tree) or
equals the new output. Any other changed file is someone's work: the commit
is refused with ``UnsavedChangesError`` naming the files, unless ``force``.
A deleted file is not counted (generating restores it). Without git, or
outside a work tree, the check is skipped silently.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import uuid
from pathlib import Path

from .errors import GeneratorError, WriteError

STAGE_MARK = ".djcfg-stage-"
OLD_MARK = ".djcfg-old-"
_MANIFEST_DIR = "django-cfg-gen"


class UnsavedChangesError(GeneratorError):
    """The output folder holds uncommitted changes the generator did not make."""


class Stage:
    """One staged replacement of an output folder. See the module docstring."""

    def __init__(self, dst: Path, path: Path, holder: Path) -> None:
        self.dst = dst
        self.path = path
        self._holder = holder

    @classmethod
    def open(cls, dst: Path | str, *, seed: bool = True) -> "Stage":
        """Create the staging folder; with ``seed`` it starts as a copy of ``dst``."""
        dst = _real(Path(dst))
        dst.parent.mkdir(parents=True, exist_ok=True)
        holder = dst.parent / f".{dst.name}{STAGE_MARK}{uuid.uuid4().hex[:8]}"
        path = holder / dst.name
        try:
            holder.mkdir()
            if seed and dst.is_dir():
                shutil.copytree(dst, path, symlinks=True)
            else:
                path.mkdir()
        except OSError as e:
            shutil.rmtree(holder, ignore_errors=True)
            raise WriteError(f"cannot stage {dst}: {e}") from e
        return cls(dst, path, holder)

    def discard(self) -> None:
        shutil.rmtree(self._holder, ignore_errors=True)

    def check(self, *, force: bool = False) -> None:
        """Raise ``UnsavedChangesError`` if the swap would lose uncommitted work."""
        if force:
            return
        blocking = unsaved_changes(self.dst, staged=self.path)
        if blocking:
            shown = "\n    ".join(blocking[:20])
            more = f"\n    ... and {len(blocking) - 20} more" if len(blocking) > 20 else ""
            raise UnsavedChangesError(
                f"{self.dst} has uncommitted changes the generator did not make; "
                f"nothing was written. Commit or move them, or rerun with --force "
                f"to overwrite:\n    {shown}{more}"
            )

    def commit(self, *, force: bool = False) -> None:
        """Check, then replace ``dst`` with the staged folder. Discards on any failure."""
        try:
            self.check(force=force)
            self._swap()
        except BaseException:
            self.discard()
            raise
        self.discard()
        record_manifest(self.dst)

    def _swap(self) -> None:
        old = self.dst.parent / f".{self.dst.name}{OLD_MARK}{uuid.uuid4().hex[:8]}"
        moved = False
        try:
            if self.dst.exists() or self.dst.is_symlink():
                os.replace(self.dst, old)
                moved = True
            os.replace(self.path, self.dst)
        except OSError as e:
            if moved and not self.dst.exists():
                os.replace(old, self.dst)
            raise WriteError(f"cannot replace {self.dst}: {e}") from e
        if moved:
            if old.is_dir() and not old.is_symlink():
                shutil.rmtree(old, ignore_errors=True)
            else:
                old.unlink(missing_ok=True)


def _real(p: Path) -> Path:
    """Absolute path with a symlinked output folder followed to its target."""
    p = p.expanduser().absolute()
    return p.resolve() if p.is_symlink() else p.parent.resolve() / p.name


# ── git guard ─────────────────────────────────────────────────────────────


def _git(args: list[str], cwd: Path) -> str | None:
    """Run git; ``None`` when git is missing or the command fails."""
    try:
        out = subprocess.run(
            ["git", *args], cwd=cwd, capture_output=True, timeout=30, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return out.stdout.decode("utf-8", "surrogateescape")


def _existing_dir(p: Path) -> Path | None:
    for cand in (p, *p.parents):
        if cand.is_dir():
            return cand
    return None


def _repo_top(dst: Path) -> Path | None:
    cwd = _existing_dir(dst)
    if cwd is None:
        return None
    top = _git(["rev-parse", "--show-toplevel"], cwd)
    return Path(top.strip()).resolve() if top and top.strip() else None


def _sha(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def _manifest_path(top: Path, dst: Path) -> Path | None:
    git_dir = _git(["rev-parse", "--git-path", _MANIFEST_DIR], top)
    if not git_dir or not git_dir.strip():
        return None
    base = Path(git_dir.strip())
    if not base.is_absolute():
        base = top / base
    key = hashlib.sha1(dst.relative_to(top).as_posix().encode()).hexdigest()[:16]
    return base / f"{key}.json"


def _load_manifest(top: Path, dst: Path) -> dict[str, str]:
    mp = _manifest_path(top, dst)
    if mp is None or not mp.is_file():
        return {}
    try:
        data = json.loads(mp.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    files = data.get("files") if isinstance(data, dict) else None
    return files if isinstance(files, dict) else {}


def record_manifest(dst: Path) -> None:
    """Remember the hash of every file the generator just wrote under ``dst``."""
    dst = _real(Path(dst))
    top = _repo_top(dst)
    if top is None:
        return
    try:
        dst.relative_to(top)
    except ValueError:
        return
    mp = _manifest_path(top, dst)
    if mp is None:
        return
    files = {
        p.relative_to(dst).as_posix(): _sha(p)
        for p in sorted(dst.rglob("*"))
        if p.is_file() and "__pycache__" not in p.parts
    }
    try:
        mp.parent.mkdir(parents=True, exist_ok=True)
        tmp = mp.with_suffix(f".{os.getpid()}.tmp")
        tmp.write_text(
            json.dumps({"output": dst.relative_to(top).as_posix(), "files": files}),
            encoding="utf-8",
        )
        os.replace(tmp, mp)
    except OSError:
        pass  # the manifest only saves a --force later; never fail a run on it


def unsaved_changes(dst: Path, *, staged: Path | None = None) -> list[str]:
    """Uncommitted changes under ``dst`` that generating would lose.

    Returns paths relative to ``dst``. Empty when git is unavailable, ``dst`` is
    not in a work tree, or every change is the generator's own (see module doc).
    """
    dst = _real(Path(dst))
    if not dst.exists():
        return []
    top = _repo_top(dst)
    if top is None:
        return []
    out = _git(
        ["status", "--porcelain=v1", "-z", "--untracked-files=all", "--", str(dst)], top
    )
    if not out:
        return []
    manifest = _load_manifest(top, dst)
    blocking: list[str] = []
    entries = out.split("\0")
    i = 0
    while i < len(entries):
        entry = entries[i]
        i += 1
        if len(entry) < 4:
            continue
        xy, rel_top = entry[:2], entry[3:]
        if "R" in xy or "C" in xy:
            i += 1  # -z puts the rename source in the next field
        if "D" in xy:
            continue  # a deleted file comes back on generation; nothing is lost
        file = top / rel_top
        try:
            rel = file.relative_to(dst).as_posix()
        except ValueError:
            continue
        if not file.is_file() or "__pycache__" in Path(rel).parts:
            continue
        digest = _sha(file)
        if digest is not None and manifest.get(rel) == digest:
            continue  # unchanged since the generator wrote it
        if staged is not None and digest is not None and _sha(staged / rel) == digest:
            continue  # generating writes the same bytes again
        blocking.append(rel)
    return sorted(blocking)


__all__ = ["Stage", "UnsavedChangesError", "record_manifest", "unsaved_changes"]
