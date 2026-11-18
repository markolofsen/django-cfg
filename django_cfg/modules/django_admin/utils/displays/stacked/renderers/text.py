"""Text renderer for stacked display items."""
from __future__ import annotations

from typing import Any

from django.utils.html import conditional_escape

from ....html import _classes as C
from .._types import TextRendererConfig  # type: ignore[import]


def render_text(value: Any, config: TextRendererConfig) -> str:
    """Render a text item with optional styling, truncation, prefix/suffix."""
    text = "" if value is None else str(value)

    truncate = config.get("truncate")
    full_value = text
    if truncate and len(text) > truncate:
        text = text[:truncate] + "…"

    prefix = config.get("prefix") or ""
    suffix = config.get("suffix") or ""
    text = f"{prefix}{text}{suffix}"

    classes = []
    if config.get("bold"):
        classes.append(C.STRONG)
    if config.get("muted"):
        classes.append(C.MUTED)
    if config.get("monospace"):
        classes.append(C.MONO)

    icon_html = ""
    if config.get("icon"):
        icon_html = f'<span class="cfg-icon">{config["icon"]}</span>'

    tooltip = ""
    if truncate and len(full_value) > truncate:
        tooltip = f'title="{conditional_escape(full_value)}"'

    class_attr = f' class="{C.join(*classes)}"' if classes else ""
    tooltip_attr = f" {tooltip}" if tooltip else ""
    return f"<span{class_attr}{tooltip_attr}>{icon_html}{conditional_escape(text)}</span>"
