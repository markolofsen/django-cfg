"""
Telegram alerting for the RQ queue-health monitor.

Maps a :class:`QueueStatus` severity to the module-level shortcuts of
``django_telegram``:

- ``critical`` -> :func:`send_alert`  (CRITICAL priority)
- ``warning``  -> :func:`send_warning` (HIGH priority)
- recovery     -> :func:`send_success` (NORMAL priority)

When ``RQHealthConfig.alert_chat_id`` is set, messages are routed to that chat
via a :class:`DjangoTelegram` instance instead of the project default.
"""

from __future__ import annotations

from typing import Optional

from django_cfg.utils import get_logger

from .evaluator import QueueStatus, Severity

logger = get_logger("rq.health")

# Relative path to the django-rq admin UI; prefixed onto context links.
RQ_ADMIN_PATH = "/django-rq/"


def _build_context(status: QueueStatus) -> dict:
    """Build the Telegram context dict from a queue status."""
    metrics = status.metrics
    ctx = metrics.as_context() if metrics is not None else {"queue": status.queue}
    ctx["status"] = status.label
    if status.overflow:
        ctx["overflow"] = True
    if status.stuck:
        ctx["stuck"] = True
    if status.breaches:
        ctx["breaches"] = ", ".join(
            f"{b.metric}={_fmt(b.value)} (>= {_fmt(b.threshold)})" for b in status.breaches
        )
    return ctx


def _fmt(value: float) -> str:
    """Format a numeric metric value compactly."""
    if isinstance(value, float) and not value.is_integer():
        return f"{value:.1f}"
    return str(int(value))


def _telegram(alert_chat_id: Optional[str]):
    """
    Return a callable triple (alert, warning, success) bound to the right chat.

    When ``alert_chat_id`` is given, a dedicated :class:`DjangoTelegram` instance
    is used so messages go to the override chat; otherwise the module-level
    shortcuts (project default chat) are used.
    """
    if alert_chat_id:
        from django_cfg.modules.django_telegram.formatters import EMOJI_MAP, format_to_yaml
        from django_cfg.modules.django_telegram.queue import MessagePriority
        from django_cfg.modules.django_telegram.service import DjangoTelegram
        from django_cfg.modules.django_telegram.types import TelegramParseMode

        telegram = DjangoTelegram(chat_id=alert_chat_id)

        def _send(emoji_key: str, title: str, message: str, context: dict, links: dict, priority: int):
            text = f"{EMOJI_MAP[emoji_key]} <b>{title}</b>\n\n{message}"
            if links:
                text += "\n\n" + "  ".join(
                    f'<a href="{url}">{label}</a>' for label, url in links.items()
                )
            if context:
                text += "\n\n<pre>" + format_to_yaml(context) + "</pre>"
            telegram.send_message(
                text,
                parse_mode=TelegramParseMode.HTML,
                priority=priority,
                fail_silently=True,
            )

        def alert(msg, context=None, links=None):
            _send("alert", "ALERT", msg, context or {}, links or {}, MessagePriority.CRITICAL)

        def warning(msg, context=None, links=None):
            _send("warning", "Warning", msg, context or {}, links or {}, MessagePriority.HIGH)

        def success(msg, details=None, links=None):
            _send("success", "Success", msg, details or {}, links or {}, MessagePriority.NORMAL)

        return alert, warning, success

    from django_cfg.modules.django_telegram.shortcuts import send_alert, send_success, send_warning

    return send_alert, send_warning, send_success


def send_queue_alert(status: QueueStatus, alert_chat_id: Optional[str] = None) -> bool:
    """
    Send a Telegram alert for a degraded queue.

    Args:
        status: The :class:`QueueStatus` (must be warning or critical).
        alert_chat_id: Optional chat ID override.

    Returns:
        True if a send was attempted, False if the status did not warrant one.
    """
    if status.is_healthy:
        return False

    send_alert, send_warning, _ = _telegram(alert_chat_id)
    context = _build_context(status)
    links = {"RQ Admin": RQ_ADMIN_PATH}
    message = f"RQ queue <b>{status.queue}</b> is {status.label.upper()}"
    if status.stuck:
        message += " — queue appears stuck"
    elif status.overflow:
        message += " — queue is overflowing"

    try:
        if status.severity >= Severity.CRITICAL:
            send_alert(message, context=context, links=links)
        else:
            send_warning(message, context=context, links=links)
        return True
    except Exception as exc:  # pragma: no cover - shortcuts already fail silently
        logger.error(f"failed to send queue alert for '{status.queue}': {exc}", exc_info=True)
        return False


def send_queue_recovery(queue: str, alert_chat_id: Optional[str] = None) -> bool:
    """
    Send a Telegram recovery (success) message for a queue back to healthy.

    Args:
        queue: Queue name.
        alert_chat_id: Optional chat ID override.

    Returns:
        True if a send was attempted.
    """
    _, _, send_success = _telegram(alert_chat_id)
    links = {"RQ Admin": RQ_ADMIN_PATH}
    try:
        send_success(
            f"RQ queue <b>{queue}</b> has recovered",
            {"queue": queue, "status": "healthy"},
            links=links,
        )
        return True
    except Exception as exc:  # pragma: no cover
        logger.error(f"failed to send recovery for '{queue}': {exc}", exc_info=True)
        return False


__all__ = [
    "send_queue_alert",
    "send_queue_recovery",
    "RQ_ADMIN_PATH",
]
