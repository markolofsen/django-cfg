"""Badge renderer for stacked display items."""
from __future__ import annotations

from typing import Any

from .._types import BadgeRendererConfig  # type: ignore[import]

_BADGE_COLORS = {
    "primary": "bg-primary-100 text-primary-700 dark:bg-primary-500/20 dark:text-primary-400",
    "secondary": "bg-base-100 text-base-700 dark:bg-base-500/20 dark:text-base-200",
    "success": "bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400",
    "danger": "bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400",
    "warning": "bg-yellow-100 text-yellow-700 dark:bg-yellow-500/20 dark:text-yellow-400",
    "info": "bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-400",
}


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

    color = _BADGE_COLORS.get(str(variant), _BADGE_COLORS["secondary"])

    icon_html = ""
    if config.get("icon"):
        icon_html = f'<span class="material-symbols-outlined text-xs mr-0.5">{config["icon"]}</span>'

    return (
        f'<span class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium {color}">'
        f"{icon_html}{value_str}</span>"
    )
