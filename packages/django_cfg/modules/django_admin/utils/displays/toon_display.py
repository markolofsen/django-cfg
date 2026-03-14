"""
TOON/JSON display utility for list_display and readonly_fields.

- list_display:    compact preview with Alpine.js expand/collapse (toon_viewer_list.html)
- readonly_fields: full collapsible <details> viewer with JSON↔TOON toggle (toon_viewer_form.html)
"""
from __future__ import annotations

import json
import logging
from typing import Any

from django.template.loader import render_to_string
from django.utils.safestring import SafeString, mark_safe

logger = logging.getLogger(__name__)


def _get_nested_value(obj: Any, field_name: str) -> Any:
    """Resolve dotted / dunder field paths on a model instance."""
    parts = field_name.replace("__", ".").split(".")
    value = obj
    for part in parts:
        if value is None:
            return None
        value = getattr(value, part, None)
        if callable(value):
            value = value()
    return value


def _to_toon(value: Any) -> str:
    """Convert value to TOON string. Falls back to JSON on error."""
    try:
        from json_toon import json_to_toon
        return json_to_toon(value)
    except Exception as exc:
        logger.debug("json_to_toon failed: %s", exc)
        return json.dumps(value, indent=2, ensure_ascii=False)


class ToonDisplay:
    """Display class for list_display and readonly_fields — TOON/JSON viewer."""

    @classmethod
    def render(cls, value: Any, config: dict | None = None) -> SafeString:
        """
        Render a JSON value as a TOON/JSON viewer.

        Automatically selects the correct template:
        - When config contains 'collapsible' key → form viewer (readonly_fields)
        - Otherwise → compact list viewer (list_display)

        Args:
            value:  Python object (dict, list, etc.)
            config: Widget config dict from ToonField.get_widget_config()

        Returns:
            Safe HTML string.
        """
        config = config or {}

        if value is None or value == "":
            return mark_safe(f'<span class="text-base-400">{config.get("empty_value", "—")}</span>')

        # Parse string JSON
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except (json.JSONDecodeError, ValueError):
                return mark_safe(f'<code class="text-xs text-red-500">Invalid JSON</code>')

        try:
            toon_text = _to_toon(value)
            json_text = json.dumps(value, indent=2, ensure_ascii=False)
        except Exception as exc:
            logger.warning("ToonDisplay.render failed: %s", exc)
            return mark_safe(f'<code class="text-xs text-red-500">Render error</code>')

        field_id = config.get("field_id", f"toon_{id(value)}")
        default_mode = config.get("default_mode", "toon")

        # Form viewer (readonly_fields context — collapsible key present)
        if "collapsible" in config:
            toon_lines = toon_text.splitlines()
            return mark_safe(render_to_string(
                "django_admin/widgets/toon_viewer_form.html",
                {
                    "toon_text": toon_text,
                    "json_text": json_text,
                    "field_id": field_id,
                    "default_mode": default_mode,
                    "collapsible": config.get("collapsible", True),
                    "default_open": config.get("default_open", False),
                    "label": config.get("label", ""),
                    "max_height": config.get("max_height", "24rem"),
                    "line_count": len(toon_lines),
                },
            ))

        # List viewer (compact, with preview + expand)
        preview_lines = config.get("preview_lines", 3)
        toon_lines = toon_text.splitlines()
        preview = "\n".join(toon_lines[:preview_lines])
        has_more = len(toon_lines) > preview_lines

        return mark_safe(render_to_string(
            "django_admin/widgets/toon_viewer_list.html",
            {
                "toon_text": toon_text,
                "json_text": json_text,
                "preview": preview,
                "has_more": has_more,
                "field_id": field_id,
                "default_mode": default_mode,
            },
        ))

    @classmethod
    def from_field(cls, obj: Any, field_name: str, config: dict | None = None) -> SafeString:
        """Render from a model instance and field name."""
        config = config or {}
        value = _get_nested_value(obj, field_name)
        pk = getattr(obj, "pk", id(obj))
        config = {**config, "field_id": f"toon_{pk}_{field_name.replace('__', '_')}"}
        return cls.render(value, config)
