"""
Telegram Types and Enums.

Type definitions for Telegram module.
"""

from enum import Enum


class TelegramParseMode(Enum):
    """Telegram message parse modes."""

    MARKDOWN = "Markdown"
    MARKDOWN_V2 = "MarkdownV2"
    HTML = "HTML"


__all__ = [
    "TelegramParseMode",
]
