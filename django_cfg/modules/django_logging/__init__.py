"""
Django Logging Modules for django_cfg.

Auto-configuring logging utilities: `get_logger()` with per-module file
logging and rotation. Django log files live under ./logs (django.log +
logs/djangocfg/<module>.log, 30-day rotation). Error-level records are
additionally captured by django_monitor (JSONL + Telegram alerts).
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
