"""
django_monitor — error capture + Telegram alerting for django-cfg.

Zero-config. Captures unhandled exceptions, ERROR logs, slow queries,
RQ failures and browser events (via /cfg/monitor/ingest/):

- every event is written as a JSON line through the standard logging
  pipeline (logs/djangocfg/monitor.log, daily rotation, 30 days — the
  same infrastructure as all django-cfg file logs);
- when TelegramConfig is set on DjangoConfig, error events are batched
  into Telegram alerts automatically. No Telegram — no alerts, nothing
  to configure either way.

Capture hooks connect automatically at startup (apps.py / cfg urls).
"""

from __future__ import annotations

import json

default_app_config = "django_cfg.modules.django_monitor.apps.DjangoMonitorConfig"

from .exceptions import MonitorConfigError, MonitorError, MonitorSyncError

_EVENT_FIELDS = (
    "fingerprint", "event_type", "level", "message", "stack_trace",
    "logger_name", "url", "http_method", "http_status",
    "func_name", "module", "lineno", "extra",
)


def is_enabled() -> bool:
    """Monitoring is always on — capture hooks self-disable under test runners."""
    return True


def _event_to_dict(event) -> dict:
    """Normalize a capture event (duck-typed object or dict) to a JSON-safe dict."""
    if isinstance(event, dict):
        raw = dict(event)
    else:
        raw = {k: getattr(event, k) for k in _EVENT_FIELDS if hasattr(event, k)}
    return {k: v for k, v in raw.items() if v not in (None, "", {}, [])}


def _log_event(stream: str, record: dict) -> None:
    """One JSON line into logs/djangocfg/monitor.log via the standard pipeline."""
    from django_cfg.modules.django_logging import get_logger

    # Fully-qualified name — get_logger uses it as-is (its caller-path
    # auto-detection would otherwise rewrite the name and misroute the file).
    get_logger(f"django_cfg.monitor.{stream}").info(
        json.dumps(record, ensure_ascii=False, default=str)
    )


def capture_server_event(event) -> None:
    """Capture a server event (log line + Telegram batch). Never raises."""
    try:
        from .capture.notify import notify_server_event

        record = _event_to_dict(event)
        _log_event("server", record)
        notify_server_event(
            record.get("event_type", ""),
            record.get("message", ""),
            record.get("extra") or {},
            fingerprint=record.get("fingerprint", ""),
        )
    except Exception:
        pass


def capture_frontend_events(events: list[dict]) -> None:
    """Capture a batch of normalized frontend events. Never raises."""
    try:
        from .capture.notify import notify_server_event

        for ev in events:
            record = _event_to_dict(ev)
            _log_event("frontend", record)
            # Error-level browser events join the same Telegram batch.
            if record.get("level") == "error":
                notify_server_event(
                    "FRONTEND_ERROR",
                    record.get("message", ""),
                    {},
                    fingerprint=record.get("fingerprint", ""),
                    api_url=record.get("url", ""),
                )
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

        capture_server_event({
            "fingerprint": fingerprint,
            "event_type": "SERVER_ERROR",
            "level": "error",
            "message": str(exc)[:2000],
            "stack_trace": stack[:10000],
            "url": url,
            "http_method": http_method,
            "func_name": func_name,
            "module": module,
            "lineno": lineno,
        })
    except Exception:
        pass


def capture_message(message: str, *, level: str = "error", extra: dict | None = None) -> None:
    """
    Public API — capture a plain message (no exception).

    Usage:
        capture_message("payment gateway timeout", level="warning", extra={"order_id": 123})
    """
    try:
        import hashlib

        fingerprint = hashlib.sha256(f"MESSAGE::{message[:100]}".encode()).hexdigest()[:16]
        capture_server_event({
            "fingerprint": fingerprint,
            "event_type": "LOG_ERROR",
            "level": level,
            "message": message[:2000],
            "extra": extra or {},
        })
    except Exception:
        pass


__all__ = [
    # Exceptions
    "MonitorError",
    "MonitorConfigError",
    "MonitorSyncError",
    # Helpers
    "is_enabled",
    # Capture
    "capture_server_event",
    "capture_frontend_events",
    # Public API
    "capture_exception",
    "capture_message",
]
