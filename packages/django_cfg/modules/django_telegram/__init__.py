"""
Django Telegram Service for django_cfg.

Auto-configuring Telegram notification service that integrates with DjangoConfig.
Supports custom bot_token and chat_id per-call with fallback to config defaults.

Module Structure:
- exceptions.py: TelegramError, TelegramConfigError, TelegramSendError
- queue.py: TelegramMessageQueue, MessagePriority, telegram_queue
- types.py: TelegramParseMode
- formatters.py: EMOJI_MAP, format_to_yaml, format_message_with_context
- shortcuts.py: send_error, send_success, send_warning, send_info, send_stats, send_alert
- service.py: DjangoTelegram
- utils.py: send_telegram_message, send_telegram_photo, send_telegram_document
"""

from .exceptions import (
    TelegramConfigError,
    TelegramError,
    TelegramSendError,
)
from .formatters import (
    EMOJI_MAP,
    format_message_with_context,
    format_to_yaml,
)
from .queue import (
    MessagePriority,
    TelegramMessageQueue,
    telegram_queue,
)
from .service import DjangoTelegram
from .shortcuts import (
    send_alert,
    send_error,
    send_info,
    send_stats,
    send_success,
    send_warning,
)
from .types import TelegramParseMode
from .utils import (
    send_telegram_document,
    send_telegram_message,
    send_telegram_photo,
)

__all__ = [
    # Exceptions
    "TelegramError",
    "TelegramConfigError",
    "TelegramSendError",
    # Queue
    "MessagePriority",
    "TelegramMessageQueue",
    "telegram_queue",
    # Types
    "TelegramParseMode",
    # Formatters
    "EMOJI_MAP",
    "format_to_yaml",
    "format_message_with_context",
    # Shortcuts
    "send_error",
    "send_success",
    "send_warning",
    "send_info",
    "send_stats",
    "send_alert",
    # Service
    "DjangoTelegram",
    # Utils
    "send_telegram_message",
    "send_telegram_photo",
    "send_telegram_document",
]
