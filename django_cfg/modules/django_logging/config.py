"""
Django ``LOGGING`` for django-cfg.

12-factor: records go to stdout/stderr and the platform routes them. A file is
opt-in (``DJANGO_CFG_LOG_DIR`` or ``logging.dir``) and is size-rotated with a bounded backup count, safe
with several workers. Nothing here runs at import time: directories are
created when the first record is written, never when the dict is built.
"""
from __future__ import annotations

import json
import logging
import os
import sys
import traceback
from logging.handlers import TimedRotatingFileHandler, WatchedFileHandler
from pathlib import Path
from typing import Any, Dict

from django_cfg.core.utils import runtime_paths as rp

TEXT_FORMAT = "[%(asctime)s] %(levelname)s in %(name)s [%(filename)s:%(lineno)d]: %(message)s"

#: ``extra`` key under which django_monitor hands its event dict to the formatter.
MONITOR_EVENT_ATTR = "monitor_event"

_STD_ATTRS = set(logging.makeLogRecord({}).__dict__) | {"message", "asctime", "taskName"}


class JsonFormatter(logging.Formatter):
    """One JSON object per line, for containers."""

    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }
        if record.exc_info:
            payload["exc"] = "".join(traceback.format_exception(*record.exc_info)).rstrip()
        for key, value in record.__dict__.items():
            if key not in _STD_ATTRS and not key.startswith("_") and key != MONITOR_EVENT_ATTR:
                payload[key] = value
        event = getattr(record, MONITOR_EVENT_ATTR, None)
        if isinstance(event, dict):
            # A django_monitor event is the record: its fields (event_type, fingerprint,
            # level, message, url, ...) sit at the top level, not as JSON inside "message".
            payload["message"] = ""
            payload.update({k: v for k, v in event.items() if k not in ("ts", "logger")})
        return json.dumps(payload, ensure_ascii=False, default=str)


class _LazyDirMixin:
    """Create the directory at first write; on failure warn once and stop writing the file
    (records still reach the console handler through propagation)."""

    _fallback = False

    def _open(self):  # type: ignore[override]
        Path(self.baseFilename).parent.mkdir(parents=True, exist_ok=True)
        return super()._open()  # type: ignore[misc]

    def emit(self, record: logging.LogRecord) -> None:  # type: ignore[override]
        if self._fallback:
            return
        try:
            super().emit(record)  # type: ignore[misc]
        except OSError as exc:
            self._fail(exc, record)

    def handleError(self, record: logging.LogRecord) -> None:  # type: ignore[override]
        exc = sys.exc_info()[1]
        if isinstance(exc, OSError):
            self._fail(exc, record)
        else:
            super().handleError(record)  # type: ignore[misc]

    def _fail(self, exc: OSError, record: logging.LogRecord) -> None:
        self._fallback = True
        rp.warn_once(
            f"log-unwritable:{self.baseFilename}",
            f"django-cfg cannot write {self.baseFilename} ({exc}); logging to stdout/stderr only.",
        )


class LazyWatchedFileHandler(_LazyDirMixin, WatchedFileHandler):
    """File handler for external logrotate (reopens on rotation). Safe with many workers."""

    def __init__(self, filename, **kwargs):
        kwargs.setdefault("encoding", "utf-8")
        super().__init__(filename, delay=True, **kwargs)


class LazySizeRotatingFileHandler(LazyWatchedFileHandler):
    """Size-based rotation that several workers can share.

    ``RotatingFileHandler`` races when more than one process writes the file: each
    renames the same path. Here the rename happens under an ``flock`` on
    ``<file>.lock`` and only if the file at the path is still over the limit, so
    exactly one worker rotates; the others notice the new inode
    (``WatchedFileHandler``) and reopen. ``maxBytes=0`` turns rotation off (leave it
    to logrotate). ``backupCount`` is the number of ``.1`` ... ``.N`` files kept.
    """

    def __init__(self, filename, maxBytes: int | None = None, backupCount: int | None = None, **kwargs):
        super().__init__(filename, **kwargs)
        self.maxBytes = rp.log_rotate_bytes() if maxBytes is None else maxBytes
        self.backupCount = rp.log_backups() if backupCount is None else backupCount

    def emit(self, record: logging.LogRecord) -> None:
        if self.maxBytes > 0 and not self._fallback:
            try:
                self._rotate_if_needed()
            except Exception:  # rotation must never lose or raise on a record
                pass
        super().emit(record)

    def _rotate_if_needed(self) -> None:
        try:
            size = os.stat(self.baseFilename).st_size
        except OSError:
            return
        if size < self.maxBytes:
            return
        try:
            import fcntl
        except ImportError:  # Windows: single-writer rotation without the lock
            fcntl = None  # type: ignore[assignment]
        lock = None
        try:
            if fcntl is not None:
                lock = open(self.baseFilename + ".lock", "a")
                fcntl.flock(lock, fcntl.LOCK_EX)
            if os.stat(self.baseFilename).st_size < self.maxBytes:
                return  # another worker rotated while we waited
            self._shift_backups()
        except OSError:
            pass
        finally:
            if lock is not None:
                lock.close()
        # The path is now a new (absent) file: reopen ours on next emit.
        self.acquire()
        try:
            if self.stream is not None:
                self.stream.close()
                self.stream = None  # type: ignore[assignment]
        finally:
            self.release()

    def _shift_backups(self) -> None:
        base = self.baseFilename
        if self.backupCount <= 0:
            os.remove(base)
            return
        oldest = f"{base}.{self.backupCount}"
        if os.path.exists(oldest):
            os.remove(oldest)
        for i in range(self.backupCount - 1, 0, -1):
            src = f"{base}.{i}"
            if os.path.exists(src):
                os.replace(src, f"{base}.{i + 1}")
        os.replace(base, f"{base}.1")


class LazyTimedRotatingFileHandler(_LazyDirMixin, TimedRotatingFileHandler):
    """Daily rotation inside the process. Single-process only: workers race on rollover.

    Kept for projects that import it; django-cfg itself uses ``LazySizeRotatingFileHandler``.
    """

    def __init__(self, filename, **kwargs):
        kwargs.setdefault("encoding", "utf-8")
        super().__init__(filename, when="midnight", backupCount=30, delay=True, **kwargs)


class NotMonitorFilter(logging.Filter):
    """Reject ``django_cfg.monitor*`` records: the monitor file already has them, and
    propagation would write each event a second time into ``django.log``."""

    def filter(self, record: logging.LogRecord) -> bool:
        return not (record.name == "django_cfg.monitor" or record.name.startswith("django_cfg.monitor."))


def resolve_level(debug: bool) -> str:
    levels = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
    value = str(rp._config_logging("level") or "").upper()
    if value not in levels:
        value = os.environ.get(rp.ENV_LOG_LEVEL, "").strip().upper()
    if value in levels:
        return value
    return "DEBUG" if debug else "WARNING"


def build_logging_config(debug: bool = False) -> Dict[str, Any]:
    """
    The ``LOGGING`` dict django-cfg generates.

    Root keeps a console handler. ``django_cfg`` gets a file only when a log directory is
    configured; ``django_cfg.monitor`` always tries its own small rotating file
    (``rp.resolve_monitor_log_dir``) and falls back to stdout alone. Propagation stays on
    so a project's own root handlers still see django-cfg records.
    """
    rp.warn_deprecated_env()
    fmt = rp.log_format()
    config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "django_cfg": (
                {"()": "django_cfg.modules.django_logging.config.JsonFormatter"}
                if fmt == "json"
                else {"format": TEXT_FORMAT}
            ),
        },
        "handlers": {
            "console": {"class": "logging.StreamHandler", "formatter": "django_cfg"},
        },
        "root": {"handlers": ["console"], "level": "INFO"},
        "loggers": {"django_cfg": {"level": resolve_level(debug), "propagate": True}},
    }

    dotted = "django_cfg.modules.django_logging.config.LazySizeRotatingFileHandler"
    log_dir = rp.resolve_log_dir()  # general logs: a file only when a directory is configured
    monitor_dir = rp.resolve_monitor_log_dir()  # monitor events: own small file, default location
    monitor_logger: Dict[str, Any] = {"level": "INFO", "propagate": True}
    if log_dir is not None:
        config["filters"] = {"not_monitor": {"()": "django_cfg.modules.django_logging.config.NotMonitorFilter"}}
        config["handlers"]["django_cfg_file"] = {
            "class": dotted,
            "filename": str(log_dir / "django.log"),
            "formatter": "django_cfg",
            "filters": ["not_monitor"],
        }
        config["loggers"]["django_cfg"]["handlers"] = ["django_cfg_file"]
    if monitor_dir is not None:
        config["handlers"]["django_cfg_monitor_file"] = {
            "class": dotted,
            "filename": str(monitor_dir / "djangocfg" / "monitor.log"),
            "formatter": "django_cfg",
        }
        monitor_logger["handlers"] = ["django_cfg_monitor_file"]
    config["loggers"]["django_cfg.monitor"] = monitor_logger
    return config


__all__ = [
    "JsonFormatter",
    "LazySizeRotatingFileHandler",
    "LazyTimedRotatingFileHandler",
    "LazyWatchedFileHandler",
    "NotMonitorFilter",
    "build_logging_config",
    "resolve_level",
]
