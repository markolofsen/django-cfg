"""
Keep django-cfg's own log files bounded.

Two entry points, one rule set:

* ``prune_log_dir`` - delete old or surplus *rotated* django-cfg files and, when the
  directory is still over its cap, the oldest rotated ones until it is not.
* ``startup_self_check`` - what runs at boot: a daemon thread, at most once per day
  per directory (a stamp file), that prunes and logs ONE clear warning if the
  directory still exceeds the cap. It never blocks boot and never raises.

Only files django-cfg writes are candidates: ``django.log*``, everything under
``djangocfg/`` and the names older versions created (``apps.log``, ``core.log``,
``telegram.log``, ``debug.log``, ``app_*.log``). A live file (the one a handler has open,
named exactly ``*.log``) is never deleted here; the size-rotating handler rotates it.
"""
from __future__ import annotations

import fnmatch
import logging
import os
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from django_cfg.core.utils import runtime_paths as rp

logger = logging.getLogger("django_cfg.logging.maintenance")

STAMP_NAME = ".django_cfg_prune"
STAMP_INTERVAL_SEC = 24 * 3600

_OWN_ROOT_PATTERNS = ("django.log", "django.log.*", "apps.log*", "core.log*", "telegram.log*", "debug.log*", "app_*.log*")
_SKIP_SUFFIXES = (".lock",)


@dataclass
class FileInfo:
    path: Path
    size: int
    mtime: float


@dataclass
class PruneResult:
    directory: Path
    total_before: int = 0
    total_after: int = 0
    cap: int = 0
    deleted: List[FileInfo] = field(default_factory=list)
    dry_run: bool = True

    @property
    def freed(self) -> int:
        return sum(f.size for f in self.deleted)

    @property
    def over_cap(self) -> bool:
        return self.cap > 0 and self.total_after > self.cap


def _is_own(rel: Path) -> bool:
    if rel.name.endswith(_SKIP_SUFFIXES) or rel.name == STAMP_NAME:
        return False
    if rel.parts and rel.parts[0] == "djangocfg":
        return True
    if len(rel.parts) != 1:
        return False
    return any(fnmatch.fnmatch(rel.name, pat) for pat in _OWN_ROOT_PATTERNS)


def _base_name(path: Path) -> str:
    """``monitor.log.3`` / ``monitor.log.2026-10-01`` -> ``monitor.log``."""
    name = path.name
    idx = name.find(".log")
    return name[: idx + 4] if idx >= 0 else name


def collect(directory: Path) -> List[FileInfo]:
    files: List[FileInfo] = []
    if not directory.is_dir():
        return files
    for path in directory.rglob("*"):
        try:
            if not path.is_file() or path.is_symlink():
                continue
            rel = path.relative_to(directory)
            if not _is_own(rel):
                continue
            st = path.stat()
            files.append(FileInfo(path, st.st_size, st.st_mtime))
        except OSError:
            continue
    return files


def dir_size(directory: Path) -> int:
    return rp._dir_size(directory)


def prune_log_dir(
    directory: Path,
    *,
    keep_days: Optional[int] = None,
    backups: Optional[int] = None,
    cap: Optional[int] = None,
    dry_run: bool = True,
    now: Optional[float] = None,
) -> PruneResult:
    """Apply the three rules (age, count per file, directory cap) to rotated files."""
    keep_days = rp.log_retain_days() if keep_days is None else keep_days
    backups = rp.log_backups() if backups is None else backups
    cap = rp.env_int(rp.ENV_LOG_DIR_MAX_BYTES, rp.DEFAULT_LOG_DIR_MAX_BYTES) if cap is None else cap
    now = time.time() if now is None else now

    result = PruneResult(directory=directory, cap=cap, dry_run=dry_run)
    files = collect(directory)
    result.total_before = sum(f.size for f in files)

    # A live file is the exact name a handler writes. Anything else is a backup or a leftover.
    def is_backup(f: FileInfo) -> bool:
        return f.path.name not in ("django.log", "monitor.log")

    candidates = [f for f in files if is_backup(f)]
    doomed: dict[Path, FileInfo] = {}

    if keep_days > 0:
        cutoff = now - keep_days * 86400
        for f in candidates:
            if f.mtime < cutoff:
                doomed[f.path] = f

    by_base: dict[tuple[Path, str], List[FileInfo]] = {}
    for f in candidates:
        if f.path not in doomed:
            by_base.setdefault((f.path.parent, _base_name(f.path)), []).append(f)
    for group in by_base.values():
        group.sort(key=lambda f: f.mtime, reverse=True)
        for f in group[backups:]:
            doomed[f.path] = f

    remaining = result.total_before - sum(f.size for f in doomed.values())
    if cap > 0 and remaining > cap:
        for f in sorted((f for f in candidates if f.path not in doomed), key=lambda f: f.mtime):
            if remaining <= cap:
                break
            doomed[f.path] = f
            remaining -= f.size

    for f in sorted(doomed.values(), key=lambda f: f.mtime):
        if not dry_run:
            try:
                f.path.unlink()
            except OSError:
                continue
        result.deleted.append(f)
    result.total_after = result.total_before - result.freed
    return result


def target_dirs() -> List[Path]:
    """Directories to look after: the configured log dir and the monitor-event dir (often the same)."""
    found: List[Path] = []
    for d in (rp.resolve_log_dir(), rp.resolve_monitor_log_dir()):
        if d is not None and d not in found:
            found.append(d)
    return found


def _stamp_due(directory: Path, now: float) -> bool:
    """True (and re-stamps) at most once per interval per directory, across workers."""
    stamp = directory / STAMP_NAME
    try:
        if stamp.exists() and now - stamp.stat().st_mtime < STAMP_INTERVAL_SEC:
            return False
        stamp.touch()
        os.utime(stamp, (now, now))
        return True
    except OSError:
        return False


def run_self_check(directory: Path) -> Optional[PruneResult]:
    """Prune ``directory`` and warn once if it is still over the cap. Never raises."""
    try:
        if not directory.is_dir() or not _stamp_due(directory, time.time()):
            return None
        result = prune_log_dir(directory, dry_run=False)
        if result.deleted:
            logger.info(
                "django-cfg pruned %d old log file(s) in %s, freed %.0f MB",
                len(result.deleted), directory, result.freed / 1048576,
            )
        if result.over_cap:
            logger.warning(
                "django-cfg log directory %s is %.0f MB, over the %.0f MB cap (%s). "
                "Rotated files were pruned; the rest is live or not django-cfg's. "
                "Lower %s / %s, or run `manage.py log_prune --dir %s`.",
                directory, result.total_after / 1048576, result.cap / 1048576, rp.ENV_LOG_DIR_MAX_BYTES,
                "logging.rotate_mb", "logging.backups", directory,
            )
        return result
    except Exception:  # boot must not depend on housekeeping
        return None


def startup_self_check(*, background: bool = True) -> Optional[threading.Thread]:
    """Boot hook: look after the log directory without ever delaying or breaking boot."""
    try:
        setting = os.environ.get(rp.ENV_LOG_PRUNE, "").strip()
        if setting and not rp.env_flag(rp.ENV_LOG_PRUNE):
            return None  # explicitly turned off (DJANGO_CFG_LOG_PRUNE=0)
        dirs = target_dirs()
        if not dirs:
            return None

        def work() -> None:
            for directory in dirs:
                run_self_check(directory)

        if not background:
            work()
            return None
        thread = threading.Thread(target=work, name="django-cfg-log-check", daemon=True)
        thread.start()
        return thread
    except Exception:
        return None


__all__ = [
    "FileInfo",
    "PruneResult",
    "collect",
    "prune_log_dir",
    "run_self_check",
    "startup_self_check",
    "target_dirs",
]
