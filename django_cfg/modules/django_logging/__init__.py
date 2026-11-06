"""
Django Logging Modules for django_cfg.

`get_logger()` plus the generated `LOGGING` dict (`config.build_logging_config`).
Records go to stdout/stderr; a file is opt-in via DJANGO_CFG_LOG_DIR
(WatchedFileHandler, external logrotate). Importing creates no files or
directories. Error-level records are additionally captured by django_monitor
(JSONL + Telegram alerts).
"""

from .django_logger import (
    RESERVED_LOG_ATTRS,
    DjangoLogger,
    clean_old_logs,
    get_logger,
    sanitize_extra,
)
from .logger import logger

__all__ = [
    "logger",
    "DjangoLogger",
    "get_logger",
    "sanitize_extra",
    "clean_old_logs",
    "RESERVED_LOG_ATTRS",
]
