"""
Django ``LOGGING`` for django-cfg.

12-factor: records go to stdout/stderr and the platform routes them. A file is
opt-in (``DJANGO_CFG_LOG_DIR``, config ``logging.log_dir``, or
``DJANGO_CFG_LOG_FILE=1``). Nothing here runs at import time: directories are
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
            if key not in _STD_ATTRS and not key.startswith("_"):
                payload[key] = value
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


class LazyTimedRotatingFileHandler(_LazyDirMixin, TimedRotatingFileHandler):
    """Daily rotation inside the process. Single-process only: workers race on rollover."""

    def __init__(self, filename, **kwargs):
        kwargs.setdefault("encoding", "utf-8")
        super().__init__(filename, when="midnight", backupCount=30, delay=True, **kwargs)


def resolve_level(debug: bool) -> str:
    value = os.environ.get(rp.ENV_LOG_LEVEL, "").strip().upper()
    if not value:
        cfg = rp._current_config()
        value = str(getattr(getattr(cfg, "logging", None), "level", "") or "").upper()
    if value in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        return value
    return "DEBUG" if debug else "WARNING"


def build_logging_config(debug: bool = False) -> Dict[str, Any]:
    """
    The ``LOGGING`` dict django-cfg generates.

    Root keeps a console handler; ``django_cfg`` and ``django_cfg.monitor``
    get file handlers only when a log directory resolves. Propagation stays on
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

    log_dir = rp.resolve_log_dir()
    if log_dir is not None:
        rotate = rp.env_flag(rp.ENV_LOG_ROTATE)
        handler_cls = "LazyTimedRotatingFileHandler" if rotate else "LazyWatchedFileHandler"
        dotted = f"django_cfg.modules.django_logging.config.{handler_cls}"
        config["handlers"]["django_cfg_file"] = {
            "class": dotted,
            "filename": str(log_dir / "django.log"),
            "formatter": "django_cfg",
        }
        config["handlers"]["django_cfg_monitor_file"] = {
            "class": dotted,
            "filename": str(log_dir / "djangocfg" / "monitor.log"),
            "formatter": "django_cfg",
        }
        config["loggers"]["django_cfg"]["handlers"] = ["django_cfg_file"]
        config["loggers"]["django_cfg.monitor"] = {
            "level": "INFO",
            "handlers": ["django_cfg_monitor_file"],
            "propagate": True,
        }
    else:
        config["loggers"]["django_cfg.monitor"] = {"level": "INFO", "propagate": True}
    return config


__all__ = [
    "JsonFormatter",
    "LazyTimedRotatingFileHandler",
    "LazyWatchedFileHandler",
    "build_logging_config",
    "resolve_level",
]
