"""
Telegram Message Formatters.

Emoji mappings and message formatting utilities.
"""

import html as _html_module
import re
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


def escape_html(text: str) -> str:
    """
    Escape user-provided text for safe embedding in HTML parse_mode messages.

    Escapes: & → &amp;  < → &lt;  > → &gt;

    Use this on any LLM-generated or user-controlled content before wrapping
    it in HTML tags for Telegram. Pre-formatted HTML (with intentional tags)
    should NOT be escaped.

    Example:
        safe = f"<b>{escape_html(user_input)}</b>"
    """
    return _html_module.escape(text, quote=False)


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
    text = f"{emoji} <b>{escape_html(title)}</b>\n\n{escape_html(message)}"
    if context:
        text += "\n\n<pre>" + _html_module.escape(format_to_yaml(context)) + "</pre>"
    return text


_MD_FENCE_RE = re.compile(r"```([\w+\-.]*)\n?(.*?)```", re.DOTALL)
_MD_INLINE_CODE_RE = re.compile(r"`([^`\n]+?)`")
_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
_MD_BOLD_RE = re.compile(r"(?<!\\)\*\*(?=\S)(.+?)(?<=\S)\*\*", re.DOTALL)
_MD_BOLD_UNDER_RE = re.compile(r"(?<!\\)__(?=\S)(.+?)(?<=\S)__", re.DOTALL)
_MD_ITALIC_RE = re.compile(r"(?<![\*\\\w])\*(?=\S)([^\*\n]+?)(?<=\S)\*(?!\*)")
_MD_ITALIC_UNDER_RE = re.compile(r"(?<![_\\\w])_(?=\S)([^_\n]+?)(?<=\S)_(?!_)")
_MD_STRIKE_RE = re.compile(r"~~(?=\S)(.+?)(?<=\S)~~", re.DOTALL)
_MD_HEADING_RE = re.compile(r"^[ \t]{0,3}#{1,6}[ \t]+(.+?)[ \t]*#*[ \t]*$", re.MULTILINE)
_MD_BULLET_RE = re.compile(r"^[ \t]*[-*+][ \t]+(.+)$", re.MULTILINE)
_MD_BLOCKQUOTE_RE = re.compile(r"(?:^&gt;[ \t]?.*(?:\n|$))+", re.MULTILINE)
_MD_BACKSLASH_ESC_RE = re.compile(r"\\([\\`*_{}\[\]()#+\-.!~>])")
_MD_PLACEHOLDER_RE = re.compile(r"\x00P(\d+)\x00")

_MD_SAFE_SCHEMES = ("http://", "https://", "tg://", "mailto:")


def markdown_to_telegram_html(text: str) -> str:
    """Convert Markdown to Telegram-safe HTML (``parse_mode=HTML``).

    Use this on AI/LLM-generated message bodies before passing to
    ``DjangoTelegram.send_message(parse_mode=HTML)``. Do NOT call this on
    already-formatted HTML built by ``format_message_with_context`` or the
    fail-silent shortcuts — they emit hand-crafted HTML that this function
    would re-escape.

    Allowed Telegram tags: b, strong, i, em, u, s, code, pre, a, blockquote,
    tg-spoiler. Everything else is escaped.
    """
    if not text:
        return ""

    placeholders: list[str] = []

    def _stash(html: str) -> str:
        placeholders.append(html)
        return f"\x00P{len(placeholders) - 1}\x00"

    def _fence(m: "re.Match[str]") -> str:
        body = m.group(2).rstrip("\n")
        return _stash(f"<pre><code>{_html_module.escape(body, quote=False)}</code></pre>")

    text = _MD_FENCE_RE.sub(_fence, text)

    def _inline(m: "re.Match[str]") -> str:
        return _stash(f"<code>{_html_module.escape(m.group(1), quote=False)}</code>")

    text = _MD_INLINE_CODE_RE.sub(_inline, text)

    def _link(m: "re.Match[str]") -> str:
        label, url = m.group(1), m.group(2)
        if not url.lower().startswith(_MD_SAFE_SCHEMES):
            return _html_module.escape(m.group(0), quote=False)
        href = _html_module.escape(url, quote=True)
        return _stash(f'<a href="{href}">{_html_module.escape(label, quote=False)}</a>')

    text = _MD_LINK_RE.sub(_link, text)

    text = _html_module.escape(text, quote=False)

    text = _MD_BOLD_RE.sub(lambda m: f"{_stash('<b>')}{m.group(1)}{_stash('</b>')}", text)
    text = _MD_BOLD_UNDER_RE.sub(lambda m: f"{_stash('<b>')}{m.group(1)}{_stash('</b>')}", text)
    text = _MD_STRIKE_RE.sub(lambda m: f"{_stash('<s>')}{m.group(1)}{_stash('</s>')}", text)
    text = _MD_ITALIC_RE.sub(lambda m: f"{_stash('<i>')}{m.group(1)}{_stash('</i>')}", text)
    text = _MD_ITALIC_UNDER_RE.sub(lambda m: f"{_stash('<i>')}{m.group(1)}{_stash('</i>')}", text)

    text = _MD_HEADING_RE.sub(lambda m: _stash(f"<b>{m.group(1).strip()}</b>"), text)
    text = _MD_BULLET_RE.sub(lambda m: f"• {m.group(1)}", text)

    def _quote(m: "re.Match[str]") -> str:
        lines = [
            re.sub(r"^&gt;[ \t]?", "", line)
            for line in m.group(0).rstrip("\n").splitlines()
        ]
        return _stash(f"<blockquote>{chr(10).join(lines)}</blockquote>") + "\n"

    text = _MD_BLOCKQUOTE_RE.sub(_quote, text)
    text = _MD_BACKSLASH_ESC_RE.sub(r"\1", text)
    text = _MD_PLACEHOLDER_RE.sub(lambda m: placeholders[int(m.group(1))], text)
    return text.strip("\n")


__all__ = [
    "EMOJI_MAP",
    "escape_html",
    "format_to_yaml",
    "format_message_with_context",
    "markdown_to_telegram_html",
]
