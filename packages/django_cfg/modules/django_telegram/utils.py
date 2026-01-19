"""
Telegram utilities and convenience functions.

Supports custom credentials per-call with fallback to config defaults.
"""

from typing import BinaryIO, Optional, Union

from .service import DjangoTelegram
from .types import TelegramParseMode


def send_telegram_message(
    message: str,
    chat_id: Optional[Union[int, str]] = None,
    bot_token: Optional[str] = None,
    parse_mode: Optional[TelegramParseMode] = None,
    fail_silently: bool = False,
) -> bool:
    """
    Send a Telegram message using auto-configured service.

    Args:
        message: Message text to send
        chat_id: Target chat ID (uses config default if not provided)
        bot_token: Custom bot token (uses config default if not provided)
        parse_mode: Message parse mode
        fail_silently: Don't raise exceptions on failure

    Returns:
        True if message queued successfully
    """
    telegram = DjangoTelegram(bot_token=bot_token, chat_id=chat_id)
    return telegram.send_message(
        message=message,
        parse_mode=parse_mode,
        fail_silently=fail_silently,
    )


def send_telegram_photo(
    photo: Union[str, BinaryIO],
    caption: Optional[str] = None,
    chat_id: Optional[Union[int, str]] = None,
    bot_token: Optional[str] = None,
    fail_silently: bool = False,
) -> bool:
    """
    Send a Telegram photo using auto-configured service.

    Args:
        photo: Photo file path, URL, or file-like object
        caption: Photo caption
        chat_id: Target chat ID (uses config default if not provided)
        bot_token: Custom bot token (uses config default if not provided)
        fail_silently: Don't raise exceptions on failure

    Returns:
        True if photo queued successfully
    """
    telegram = DjangoTelegram(bot_token=bot_token, chat_id=chat_id)
    return telegram.send_photo(
        photo=photo,
        caption=caption,
        fail_silently=fail_silently,
    )


def send_telegram_document(
    document: Union[str, BinaryIO],
    caption: Optional[str] = None,
    chat_id: Optional[Union[int, str]] = None,
    bot_token: Optional[str] = None,
    fail_silently: bool = False,
) -> bool:
    """
    Send a Telegram document using auto-configured service.

    Args:
        document: Document file path, URL, or file-like object
        caption: Document caption
        chat_id: Target chat ID (uses config default if not provided)
        bot_token: Custom bot token (uses config default if not provided)
        fail_silently: Don't raise exceptions on failure

    Returns:
        True if document queued successfully
    """
    telegram = DjangoTelegram(bot_token=bot_token, chat_id=chat_id)
    return telegram.send_document(
        document=document,
        caption=caption,
        fail_silently=fail_silently,
    )


__all__ = [
    "send_telegram_message",
    "send_telegram_photo",
    "send_telegram_document",
]
