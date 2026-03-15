"""Money renderer for stacked display items."""
from __future__ import annotations

from typing import Any


def render_money(obj: Any, field_name: str, config: dict) -> str:
    """Render a money field item using full_display property or raw value."""
    full_display_field = f"{field_name}_full_display"
    if hasattr(obj, full_display_field):
        value = getattr(obj, full_display_field)
        if value:
            return f'<span class="text-sm font-medium">{value}</span>'

    value = getattr(obj, field_name, None)
    if value is None:
        return ""
    return f'<span class="text-sm font-medium">{value:,.2f}</span>'
