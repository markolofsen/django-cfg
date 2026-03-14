"""Text renderer for stacked display items."""
from __future__ import annotations

from typing import Any

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

    classes = ["text-sm"]
    if config.get("bold"):
        classes.append("font-semibold")
    if config.get("muted"):
        classes.append("text-font-subtle-light dark:text-font-subtle-dark")
    if config.get("monospace"):
        classes.append("font-mono")

    icon_html = ""
    if config.get("icon"):
        icon_html = f'<span class="material-symbols-outlined text-sm mr-1">{config["icon"]}</span>'

    tooltip = ""
    if truncate and len(full_value) > truncate:
        tooltip = f'title="{full_value}"'

    return f'<span class="{" ".join(classes)}" {tooltip}>{icon_html}{text}</span>'
