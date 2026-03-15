"""
django_monitor — D1-only monitor module for django-cfg.

Captures ServerEvent and FrontendEvent to Cloudflare D1 via django_cf.
No PostgreSQL required — works even when the main database is unavailable.

Usage in djangoconfig.py:
    from django_cfg.modules.django_cf import CloudflareConfig

    class MyConfig(DjangoConfig):
        cloudflare: CloudflareConfig = CloudflareConfig(
            enabled=True,
            account_id="${CF_ACCOUNT_ID}",
            api_token="${CF_API_TOKEN}",
            d1_database_id="${CF_D1_DATABASE_ID}",
        )

Then connect capture hooks at startup:
    from django_cfg.modules.django_monitor.capture import connect_capture
    connect_capture()
"""

from __future__ import annotations

default_app_config = "django_cfg.modules.django_monitor.apps.DjangoMonitorConfig"

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .events.service import MonitorSyncService

from .exceptions import MonitorConfigError, MonitorError, MonitorSyncError

_service_instance: Optional["MonitorSyncService"] = None


def is_enabled() -> bool:
    """Return True when django_cf is configured and ready."""
    try:
        from django_cfg.modules.django_cf import is_ready
        return is_ready()
    except Exception:
        return False


def get_service() -> "MonitorSyncService":
    """Return (cached) MonitorSyncService instance.

    Raises MonitorConfigError if django_cf is not configured.
    """
    global _service_instance
    if _service_instance is None:
        if not is_enabled():
            raise MonitorConfigError(
                "django_monitor: django_cf is not configured",
                suggestion="Add CloudflareConfig(enabled=True, ...) to DjangoConfig",
            )
        from .events.service import MonitorSyncService
        _service_instance = MonitorSyncService()
    return _service_instance


def reset_service() -> None:
    """Reset cached service instance (useful in tests)."""
    global _service_instance
    _service_instance = None


def capture_server_event(event) -> None:
    """Capture a ServerEvent to D1. Never raises — silently suppresses errors."""
    if not is_enabled():
        return
    try:
        get_service().push_server_event(event)
    except Exception:
        pass


def capture_frontend_event(event) -> None:
    """Capture a FrontendEvent to D1. Never raises — silently suppresses errors."""
    if not is_enabled():
        return
    try:
        get_service().push_frontend_event(event)
    except Exception:
        pass


def capture_exception(exc: BaseException, *, url: str = "", http_method: str = "") -> None:
    """
    Public API — capture any exception directly from app code.

    Usage:
        try:
            risky_operation()
        except Exception as e:
            capture_exception(e)
    """
    if not is_enabled():
        return
    try:
        import hashlib
        import traceback

        exc_type = type(exc)
        module = getattr(exc_type, "__module__", "") or ""
        qualname = getattr(exc_type, "__qualname__", exc_type.__name__)
        tb = exc.__traceback__
        func_name = ""
        lineno = None
        if tb:
            frames = traceback.extract_tb(tb)
            if frames:
                func_name = frames[-1].name or ""
                lineno = frames[-1].lineno

        fingerprint = hashlib.sha256(
            f"{qualname}::{module}::{func_name}".encode()
        ).hexdigest()[:16]
        stack = "".join(traceback.format_exception(exc_type, exc, tb))

        class _Event:
            pass

        ev = _Event()
        ev.fingerprint = fingerprint
        ev.event_type = "SERVER_ERROR"
        ev.level = "error"
        ev.message = str(exc)[:2000]
        ev.stack_trace = stack[:10000]
        ev.logger_name = ""
        ev.url = url
        ev.http_method = http_method
        ev.http_status = None
        ev.func_name = func_name
        ev.module = module
        ev.lineno = lineno
        ev.extra = {}
        ev.first_seen = None
        ev.last_seen = None

        get_service().push_server_event(ev)
    except Exception:
        pass


def capture_message(message: str, *, level: str = "error", extra: dict | None = None) -> None:
    """
    Public API — capture a plain message (no exception).

    Usage:
        capture_message("payment gateway timeout", level="warning", extra={"order_id": 123})
    """
    if not is_enabled():
        return
    try:
        import hashlib

        fingerprint = hashlib.sha256(f"MESSAGE::{message[:100]}".encode()).hexdigest()[:16]

        class _Event:
            pass

        ev = _Event()
        ev.fingerprint = fingerprint
        ev.event_type = "LOG_ERROR"
        ev.level = level
        ev.message = message[:2000]
        ev.stack_trace = ""
        ev.logger_name = ""
        ev.url = ""
        ev.http_method = ""
        ev.http_status = None
        ev.func_name = ""
        ev.module = ""
        ev.lineno = None
        ev.extra = extra or {}
        ev.first_seen = None
        ev.last_seen = None

        get_service().push_server_event(ev)
    except Exception:
        pass


__all__ = [
    # Exceptions
    "MonitorError",
    "MonitorConfigError",
    "MonitorSyncError",
    # Helpers
    "is_enabled",
    "get_service",
    "reset_service",
    # Capture (ORM events)
    "capture_server_event",
    "capture_frontend_event",
    # Public API
    "capture_exception",
    "capture_message",
]
