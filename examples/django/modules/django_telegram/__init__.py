"""
Django Telegram Service for django_cfg.

Auto-configuring Telegram notification service that integrates with DjangoConfig.
"""

from .service import (
    TelegramParseMode,
    TelegramError,
    TelegramConfigError,
    TelegramSendError,
    DjangoTelegram,
)
from .utils import (
    send_telegram_message,
    send_telegram_photo,
    send_telegram_document,
)

__all__ = [
    "TelegramParseMode",
    "TelegramError",
    "TelegramConfigError",
    "TelegramSendError",
    "DjangoTelegram",
    "send_telegram_message",
    "send_telegram_photo",
    "send_telegram_document",
]
