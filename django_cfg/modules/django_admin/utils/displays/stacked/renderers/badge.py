"""Badge renderer for stacked display items."""
from __future__ import annotations

from typing import Any

from django.utils.html import conditional_escape

from ....html import _classes as C
from .._types import BadgeRendererConfig  # type: ignore[import]


def render_badge(value: Any, config: BadgeRendererConfig) -> str:
    """Render a badge item with variant, label_map, optional icon."""
    if value is None:
        return ""

    if isinstance(value, bool):
        if value:
            value_str = config.get("true_label") or ""
            if not value_str:
                return ""
        else:
            value_str = config.get("false_label") or ""
            if not value_str:
                return ""
    else:
        value_str = str(value)

    variant = config.get("variant", "secondary")
    label_map = config.get("label_map") or {}
    if value in label_map:
        variant = label_map[value]
    elif value_str.lower() in label_map:
        variant = label_map[value_str.lower()]

    css = C.badge(variant, default="neutral")

    icon_html = ""
    if config.get("icon"):
        icon_html = f'<span class="cfg-icon">{conditional_escape(config["icon"])}</span>'

    return f'<span class="{css}">{icon_html}{conditional_escape(value_str)}</span>'
