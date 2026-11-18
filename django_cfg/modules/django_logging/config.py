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

from .redact import DEFAULT_REDACT_KEYS, MASK, redact
from .redact import _is_secret as _secret_key_impl


def _secret_key(key: Any, keys: tuple) -> bool:
    return _secret_key_impl(key, tuple(str(k).lower().replace("-", "_") for k in keys))

TEXT_FORMAT = "[%(asctime)s] %(levelname)s in %(name)s [%(filename)s:%(lineno)d]: %(message)s"

#: Short readable line for a development server.
SHORT_FORMAT = "%(levelname)-7s %(name)s: %(message)s"

#: ``extra`` key under which django_monitor hands its event dict to the formatter.
MONITOR_EVENT_ATTR = "monitor_event"

_STD_ATTRS = set(logging.makeLogRecord({}).__dict__) | {"message", "asctime", "taskName"}


class JsonFormatter(logging.Formatter):
    """One JSON object per line, for containers. Values of secret-looking keys are masked."""

    def __init__(self, *args: Any, redact_keys=None, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._redact_keys = tuple(DEFAULT_REDACT_KEYS) + tuple(redact_keys or ())

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
                payload[key] = MASK if _secret_key(key, self._redact_keys) else redact(value, self._redact_keys)
        event = getattr(record, MONITOR_EVENT_ATTR, None)
        if isinstance(event, dict):
            # A django_monitor event is the record: its fields (event_type, fingerprint,
            # level, message, url, ...) sit at the top level, not as JSON inside "message".
            payload["message"] = ""
            payload.update({k: v for k, v in redact(event, self._redact_keys).items() if k not in ("ts", "logger")})
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


def _env_name(environment: Any) -> str:
    value = getattr(environment, "value", environment)
    return str(value or "").strip().lower()


def _explicit_level() -> str:
    levels = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
    value = str(rp._config_logging("level") or "").upper()
    if value not in levels:
        value = os.environ.get(rp.ENV_LOG_LEVEL, "").strip().upper()
    return value if value in levels else ""


def resolve_level(debug: bool = False, environment: Any = None) -> str:
    """
    Level of the ``django_cfg`` logger.

    1. Explicit: ``logging.level`` in config, then ``DJANGO_CFG_LOG_LEVEL``. Only these give DEBUG.
    2. Otherwise by environment (``DjangoConfig.env_mode``) and command:

       - development dev server (``runserver`` ...): ``INFO``
       - everything else (production, tests, ``shell``, ``migrate``, workers): ``WARNING``

    Django ``DEBUG`` does not raise the level; ``debug`` is accepted for compatibility only.
    """
    value = _explicit_level()
    if value:
        return value
    if _env_name(environment) == "development" and rp.is_dev_server_command():
        return "INFO"
    return "WARNING"


#: Third-party loggers quieted to WARNING by default; ``DjangoLoggingConfig.log_levels`` overrides.
#: Evidence: rq.worker housekeeping was most of a carapis worker's lines; httpx/urllib3 log one line
#: per request at INFO. No grpc entries (the gRPC module is archived).
DEFAULT_LOG_LEVELS: Dict[str, str] = {
    "httpx": "WARNING",
    "httpcore": "WARNING",
    "urllib3": "WARNING",
    "asyncio": "WARNING",
    "rq": "WARNING",
    "botocore": "WARNING",
    "PIL": "WARNING",
    "django.db.backends": "WARNING",
    "django.request": "WARNING",
}

#: Loggers that own a handler of their own in Django / uvicorn / gunicorn. They lose it and
#: propagate to the root console handler, so one record is one line and one format.
SERVER_LOGGERS = (
    "django.server", "uvicorn", "uvicorn.error", "uvicorn.access",
    "gunicorn", "gunicorn.error", "gunicorn.access",
)

_CTX = "django_cfg.modules.django_logging.filters.ContextFilter"
_JUNK = "django_cfg.modules.django_logging.filters.AccessJunkFilter"


def _levels(extra: Any) -> Dict[str, str]:
    out = dict(DEFAULT_LOG_LEVELS)
    for name, lvl in (extra or {}).items():
        out[str(name)] = str(lvl).upper()
    return out


def build_logging_config(debug: bool = False, environment: Any = None) -> Dict[str, Any]:
    """
    The ``LOGGING`` dict django-cfg generates: one complete path.

    - exactly one handler on ``root``: a console handler (stderr) that applies the access-log
      junk filter, adds correlation ids, collapses repeats and formats (JSON or text);
    - ``django.server`` / ``uvicorn*`` / ``gunicorn*`` lose their own handlers and propagate to it;
    - ``django_cfg`` gets a file only when a log directory is configured; ``django_cfg.monitor``
      always tries its own small rotating file and falls back to stdout alone;
    - third-party loggers sit at the ``DEFAULT_LOG_LEVELS`` unless ``logging.log_levels`` says otherwise.
    """
    rp.warn_deprecated_env()
    fmt = rp.log_format()
    env = _env_name(environment)
    level = resolve_level(debug, environment)
    # In the test environment the ``django_cfg`` logger owns no level of its own (it inherits root's), unless a
    # level is configured explicitly. A pinned WARNING there drops INFO and DEBUG records before any handler
    # sees them, so ``caplog.at_level(INFO)`` (which sets root only) captured nothing from our own code.
    inherit_level = env == "test" and not _explicit_level()
    short = fmt == "text" and env == "development" and rp.is_dev_server_command()
    collapse_cfg = rp._config_logging("collapse")
    collapse_on = getattr(collapse_cfg, "enabled", None)
    if collapse_on is None:
        collapse_on = env != "test"
    redact_keys = list(rp._config_logging("redact_keys") or [])
    ignore = rp._config_logging("access_ignore_paths")
    junk: Dict[str, Any] = {"()": _JUNK}
    if ignore is not None:
        junk["paths"] = list(ignore)
    config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "context": {"()": _CTX},
            "access_junk": junk,
            "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        },
        "formatters": {
            "django_cfg": (
                {"()": "django_cfg.modules.django_logging.config.JsonFormatter", "redact_keys": redact_keys}
                if fmt == "json"
                else {"format": SHORT_FORMAT if short else TEXT_FORMAT}
            ),
        },
        "handlers": {
            "console": {
                "()": "django_cfg.modules.django_logging.collapse.CollapsingStreamHandler",
                "formatter": "django_cfg",
                "filters": ["access_junk", "context"],
                "collapse": bool(collapse_on),
                "window_seconds": float(getattr(collapse_cfg, "window_seconds", 60.0) or 60.0),
                "max_keys": int(getattr(collapse_cfg, "max_keys", 1000) or 1000),
            },
            # Django's own admin-mail handler, kept (it only acts when ADMINS is set and DEBUG is off).
            "mail_admins": {
                "level": "ERROR",
                "filters": ["require_debug_false"],
                "class": "django.utils.log.AdminEmailHandler",
            },
        },
        # Root follows the resolved level (never below INFO), so other libraries' INFO does not
        # reach a `shell` or a worker either.
        "root": {"handlers": ["console"], "level": "INFO" if level in ("DEBUG", "INFO") else level},
        "loggers": {
            "django": {"handlers": ["mail_admins"], "propagate": True},
            "django_cfg": {"propagate": True} if inherit_level else {"level": level, "propagate": True},
        },
    }
    for name in SERVER_LOGGERS:
        config["loggers"][name] = {"handlers": [], "propagate": True}
    for name, lvl in _levels(rp._config_logging("log_levels")).items():
        config["loggers"].setdefault(name, {"propagate": True})["level"] = lvl

    dotted = "django_cfg.modules.django_logging.config.LazySizeRotatingFileHandler"
    log_dir = rp.resolve_log_dir()  # general logs: a file only when a directory is configured
    monitor_dir = rp.resolve_monitor_log_dir()  # monitor events: own small file, default location
    monitor_logger: Dict[str, Any] = {"level": "INFO", "propagate": True}
    if log_dir is not None:
        config["filters"]["not_monitor"] = {"()": "django_cfg.modules.django_logging.config.NotMonitorFilter"}
        config["handlers"]["django_cfg_file"] = {
            "class": dotted,
            "filename": str(log_dir / "django.log"),
            "formatter": "django_cfg",
            "filters": ["not_monitor", "context"],
        }
        config["loggers"]["django_cfg"]["handlers"] = ["django_cfg_file"]
    if monitor_dir is not None:
        config["handlers"]["django_cfg_monitor_file"] = {
            "class": dotted,
            "filename": str(monitor_dir / "djangocfg" / "monitor.log"),
            "formatter": "django_cfg",
            "filters": ["context"],
        }
        monitor_logger["handlers"] = ["django_cfg_monitor_file"]
    config["loggers"]["django_cfg.monitor"] = monitor_logger
    return config


__all__ = [
    "DEFAULT_LOG_LEVELS",
    "JsonFormatter",
    "LazySizeRotatingFileHandler",
    "LazyTimedRotatingFileHandler",
    "LazyWatchedFileHandler",
    "NotMonitorFilter",
    "build_logging_config",
    "resolve_level",
]
