"""DateTime renderer for stacked display items."""
from __future__ import annotations

from typing import Any

from .._types import DateTimeItemConfig  # type: ignore[import]


def render_datetime(value: Any, config: DateTimeItemConfig) -> str:
    """Render a datetime item with optional relative time."""
    if value is None:
        return ""

    from django.utils import timezone
    from django.utils.timesince import timesince

    classes = ["text-xs"]
    if config.get("muted", True):
        classes.append("text-font-subtle-light dark:text-font-subtle-dark")

    if config.get("show_relative", False):
        try:
            text = f"{timesince(value, timezone.now())} ago"
        except Exception:
            text = str(value)
    else:
        try:
            text = value.strftime("%Y-%m-%d %H:%M")
        except Exception:
            text = str(value)

    return f'<span class="{" ".join(classes)}">{text}</span>'
