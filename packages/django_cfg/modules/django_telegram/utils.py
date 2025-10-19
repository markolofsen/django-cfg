"""
Telegram utilities and convenience functions.
"""

from typing import BinaryIO, Optional, Union

from .service import DjangoTelegram, TelegramParseMode


def send_telegram_message(
    message: str,
    chat_id: Optional[Union[int, str]] = None,
    parse_mode: Optional[TelegramParseMode] = None,
    fail_silently: bool = False,
) -> bool:
    """Send a Telegram message using auto-configured service."""
    telegram = DjangoTelegram()
    return telegram.send_message(
        message=message,
        chat_id=chat_id,
        parse_mode=parse_mode,
        fail_silently=fail_silently,
    )


def send_telegram_photo(
    photo: Union[str, BinaryIO],
    caption: Optional[str] = None,
    chat_id: Optional[Union[int, str]] = None,
    fail_silently: bool = False,
) -> bool:
    """Send a Telegram photo using auto-configured service."""
    telegram = DjangoTelegram()
    return telegram.send_photo(
        photo=photo,
        caption=caption,
        chat_id=chat_id,
        fail_silently=fail_silently,
    )


def send_telegram_document(
    document: Union[str, BinaryIO],
    caption: Optional[str] = None,
    chat_id: Optional[Union[int, str]] = None,
    fail_silently: bool = False,
) -> bool:
    """Send a Telegram document using auto-configured service."""
    telegram = DjangoTelegram()
    return telegram.send_document(
        document=document,
        caption=caption,
        chat_id=chat_id,
        fail_silently=fail_silently,
    )


__all__ = [
    "send_telegram_message",
    "send_telegram_photo",
    "send_telegram_document",
]
