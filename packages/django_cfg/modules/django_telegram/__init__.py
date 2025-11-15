"""
Django Telegram Service for django_cfg.

Auto-configuring Telegram notification service that integrates with DjangoConfig.
"""

from .service import (
    DjangoTelegram,
    MessagePriority,
    TelegramConfigError,
    TelegramError,
    TelegramParseMode,
    TelegramSendError,
)
from .utils import (
    send_telegram_document,
    send_telegram_message,
    send_telegram_photo,
)

__all__ = [
    "TelegramParseMode",
    "TelegramError",
    "TelegramConfigError",
    "TelegramSendError",
    "DjangoTelegram",
    "MessagePriority",
    "send_telegram_message",
    "send_telegram_photo",
    "send_telegram_document",
]
