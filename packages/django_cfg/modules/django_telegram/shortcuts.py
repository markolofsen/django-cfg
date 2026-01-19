"""
Telegram Shortcut Functions.

Convenience functions for common notification patterns.
All functions use default config and fail silently.
"""

from typing import Any, Dict, Optional

from .formatters import EMOJI_MAP, format_to_yaml
from .queue import MessagePriority
from .types import TelegramParseMode


def send_error(error: str, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Send error notification with HIGH priority.

    Args:
        error: Error message
        context: Optional context dict to include
    """
    try:
        from .service import DjangoTelegram

        telegram = DjangoTelegram()
        text = f"{EMOJI_MAP['error']} <b>Error</b>\n\n{error}"
        if context:
            text += "\n\n<pre>" + format_to_yaml(context) + "</pre>"
        telegram.send_message(
            text,
            parse_mode=TelegramParseMode.HTML,
            priority=MessagePriority.HIGH,
            fail_silently=True,
        )
    except Exception:
        pass


def send_success(message: str, details: Optional[Dict[str, Any]] = None) -> None:
    """
    Send success notification with NORMAL priority.

    Args:
        message: Success message
        details: Optional details dict to include
    """
    try:
        from .service import DjangoTelegram

        telegram = DjangoTelegram()
        text = f"{EMOJI_MAP['success']} <b>Success</b>\n\n{message}"
        if details:
            text += "\n\n<pre>" + format_to_yaml(details) + "</pre>"
        telegram.send_message(
            text,
            parse_mode=TelegramParseMode.HTML,
            priority=MessagePriority.NORMAL,
            fail_silently=True,
        )
    except Exception:
        pass


def send_warning(warning: str, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Send warning notification with HIGH priority.

    Args:
        warning: Warning message
        context: Optional context dict to include
    """
    try:
        from .service import DjangoTelegram

        telegram = DjangoTelegram()
        text = f"{EMOJI_MAP['warning']} <b>Warning</b>\n\n{warning}"
        if context:
            text += "\n\n<pre>" + format_to_yaml(context) + "</pre>"
        telegram.send_message(
            text,
            parse_mode=TelegramParseMode.HTML,
            priority=MessagePriority.HIGH,
            fail_silently=True,
        )
    except Exception:
        pass


def send_info(message: str, data: Optional[Dict[str, Any]] = None) -> None:
    """
    Send informational message with NORMAL priority.

    Args:
        message: Info message
        data: Optional data dict to include
    """
    try:
        from .service import DjangoTelegram

        telegram = DjangoTelegram()
        text = f"{EMOJI_MAP['info']} <b>Info</b>\n\n{message}"
        if data:
            text += "\n\n<pre>" + format_to_yaml(data) + "</pre>"
        telegram.send_message(
            text,
            parse_mode=TelegramParseMode.HTML,
            priority=MessagePriority.NORMAL,
            fail_silently=True,
        )
    except Exception:
        pass


def send_stats(title: str, stats: Dict[str, Any]) -> None:
    """
    Send statistics data with LOW priority.

    Args:
        title: Stats title
        stats: Stats dict to format
    """
    try:
        from .service import DjangoTelegram

        telegram = DjangoTelegram()
        text = f"{EMOJI_MAP['stats']} <b>{title}</b>"
        text += "\n\n<pre>" + format_to_yaml(stats) + "</pre>"
        telegram.send_message(
            text,
            parse_mode=TelegramParseMode.HTML,
            priority=MessagePriority.LOW,
            fail_silently=True,
        )
    except Exception:
        pass


def send_alert(message: str, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Send critical alert with CRITICAL priority.

    Args:
        message: Alert message
        context: Optional context dict to include
    """
    try:
        from .service import DjangoTelegram

        telegram = DjangoTelegram()
        text = f"{EMOJI_MAP['alert']} <b>ALERT</b>\n\n{message}"
        if context:
            text += "\n\n<pre>" + format_to_yaml(context) + "</pre>"
        telegram.send_message(
            text,
            parse_mode=TelegramParseMode.HTML,
            priority=MessagePriority.CRITICAL,
            fail_silently=True,
        )
    except Exception:
        pass


__all__ = [
    "send_error",
    "send_success",
    "send_warning",
    "send_info",
    "send_stats",
    "send_alert",
]
