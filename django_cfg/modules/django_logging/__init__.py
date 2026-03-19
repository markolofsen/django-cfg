"""
Django Logging Modules for django_cfg.

Auto-configuring logging utilities with optional D1 persistence.
"""

from .django_logger import (
    RESERVED_LOG_ATTRS,
    DjangoLogger,
    clean_old_logs,
    get_logger,
    sanitize_extra,
)
from .logger import logger


def is_enabled() -> bool:
    """Return True if D1 logging persistence is active."""
    try:
        from django_cfg.modules.django_cf import is_ready
        from .__cfg__ import settings as cfg
        return cfg.d1_enabled and is_ready()
    except Exception:
        return False


_service_instance = None


def get_service():
    """Return cached LogSyncService instance."""
    global _service_instance
    if _service_instance is None:
        from .core.service import LogSyncService
        _service_instance = LogSyncService()
    return _service_instance


def reset_service() -> None:
    """Clear cached service (for tests)."""
    global _service_instance
    _service_instance = None


__all__ = [
    "logger",
    "DjangoLogger",
    "get_logger",
    "sanitize_extra",
    "clean_old_logs",
    "RESERVED_LOG_ATTRS",
    "is_enabled",
    "get_service",
    "reset_service",
]
