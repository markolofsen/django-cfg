"""
Telegram Message Formatters.

Emoji mappings and message formatting utilities.
"""

from typing import Any, Dict

import yaml

from ..django_logging import get_logger

logger = get_logger("django_cfg.telegram.formatters")


# Emoji mappings for different message types
EMOJI_MAP = {
    "success": "\u2705",      # ✅
    "error": "\u274c",        # ❌
    "warning": "\u26a0\ufe0f", # ⚠️
    "info": "\u2139\ufe0f",   # ℹ️
    "start": "\U0001f680",    # 🚀
    "finish": "\U0001f3c1",   # 🏁
    "stats": "\U0001f4ca",    # 📊
    "alert": "\U0001f6a8",    # 🚨
}


def format_to_yaml(data: Dict[str, Any]) -> str:
    """
    Format dictionary data as YAML string.

    Args:
        data: Dictionary to format

    Returns:
        YAML formatted string
    """
    try:
        yaml_str = yaml.safe_dump(
            data,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            indent=2,
        )
        return yaml_str
    except Exception as e:
        logger.error(f"Error formatting to YAML: {str(e)}")
        return str(data)


def format_message_with_context(
    emoji_key: str,
    title: str,
    message: str,
    context: Dict[str, Any] | None = None,
) -> str:
    """
    Format a message with emoji, title, and optional context.

    Args:
        emoji_key: Key from EMOJI_MAP
        title: Bold title text
        message: Main message body
        context: Optional context dict to format as YAML

    Returns:
        HTML formatted message
    """
    emoji = EMOJI_MAP.get(emoji_key, "")
    text = f"{emoji} <b>{title}</b>\n\n{message}"
    if context:
        text += "\n\n<pre>" + format_to_yaml(context) + "</pre>"
    return text


__all__ = [
    "EMOJI_MAP",
    "format_to_yaml",
    "format_message_with_context",
]
