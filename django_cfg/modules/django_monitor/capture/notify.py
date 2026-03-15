"""
django_monitor.capture.notify — Telegram notifications for monitor events.

Sends alerts when critical server events are captured:
- UNHANDLED_EXCEPTION / SERVER_ERROR / RQ_FAILURE → send_error()
- SLOW_QUERY (threshold exceeded) → send_warning()

All functions fail silently — never break the capture flow.

Requires django_telegram module and CloudflareConfig.telegram_alerts_enabled=True
(read from CloudflareConfig, falls back to False if not set).
"""

from __future__ import annotations

import logging

from django_cfg.modules.django_cf import _get_config

logger = logging.getLogger(__name__)

_ALERT_EVENT_TYPES = frozenset({"UNHANDLED_EXCEPTION", "SERVER_ERROR", "RQ_FAILURE", "LOG_ERROR"})
_SLOW_QUERY_ALERT_MS: float = 5000.0  # only alert if query > 5s (above basic threshold)


def notify_server_event(event_type: str, message: str, extra: dict) -> None:
    """
    Send a Telegram notification for a captured server event.
    Called after successful D1 push — never raises.
    """
    try:
        if not _is_alerts_enabled():
            return
        if event_type in _ALERT_EVENT_TYPES:
            _send_error_alert(event_type, message, extra)
        elif event_type == "SLOW_QUERY":
            elapsed = extra.get("elapsed_ms", 0)
            if elapsed >= _SLOW_QUERY_ALERT_MS:
                _send_slow_query_alert(message, extra)
    except Exception as exc:
        logger.debug("django_monitor: notify_server_event suppressed — %s", exc)


def _is_alerts_enabled() -> bool:
    try:
        config = _get_config()
        return bool(config and getattr(config, "telegram_alerts_enabled", False))
    except Exception:
        return False


def _send_error_alert(event_type: str, message: str, extra: dict) -> None:
    from django_cfg.modules.django_telegram import send_error
    send_error(
        f"[{event_type}] {message[:300]}",
        context={k: str(v)[:200] for k, v in extra.items()} if extra else None,
    )


def _send_slow_query_alert(message: str, extra: dict) -> None:
    from django_cfg.modules.django_telegram import send_warning
    send_warning(
        message[:300],
        context={k: str(v)[:200] for k, v in extra.items()} if extra else None,
    )
