"""
Telegram Exception Classes.

Custom exceptions for Telegram-related errors.
"""


class TelegramError(Exception):
    """Base exception for Telegram-related errors."""

    pass


class TelegramConfigError(TelegramError):
    """Raised when configuration is missing or invalid."""

    pass


class TelegramSendError(TelegramError):
    """Raised when message sending fails."""

    pass


__all__ = [
    "TelegramError",
    "TelegramConfigError",
    "TelegramSendError",
]
