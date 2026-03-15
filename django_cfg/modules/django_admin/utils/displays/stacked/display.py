"""
StackedDisplay — orchestrator for multi-field stacked column display.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from django.template.loader import render_to_string
from django.utils.safestring import SafeString

from .renderers import render_badge, render_datetime, render_money, render_text


class StackedDisplay:
    """
    Display utility for stacked/composite field display.

    Renders multiple data points in a single column with rows.
    """

    @classmethod
    def render(
        cls,
        rows_data: List[Union[Dict[str, Any], List[Dict[str, Any]]]],
        config: Optional[Dict[str, Any]] = None,
    ) -> SafeString:
        """
        Render stacked display.

        Args:
            rows_data: List of row data. Each item is either:
                - A dict with 'html' key (single item row)
                - A list of dicts (inline row with multiple items)
            config: Layout options (gap, inline_gap, align, min_width, max_width)
        """
        cfg = config or {}
        context = {
            "rows": rows_data,
            "gap": cfg.get("gap", "0.25rem"),
            "inline_gap": cfg.get("inline_gap", "0.5rem"),
            "align": cfg.get("align", "left"),
            "min_width": cfg.get("min_width"),
            "max_width": cfg.get("max_width", "300px"),
        }
        return render_to_string("django_admin/widgets/stacked_display.html", context)  # type: ignore[return-value]

    @classmethod
    def from_field(
        cls,
        obj: Any,
        field: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> SafeString:
        """
        Render stacked display from model object.

        Args:
            obj: Model instance
            field: Virtual field name (unused — rows define actual fields)
            config: Configuration with 'rows' defining the layout
        """
        cfg = config or {}
        rows_config = cfg.get("rows", [])

        if not rows_config:
            return cfg.get("empty_value", "—")  # type: ignore[return-value]

        rows_data: list = []
        for row_config in rows_config:
            if isinstance(row_config, list):
                inline_items = [
                    {"html": h}
                    for item_cfg in row_config
                    if (h := cls._render_item(obj, item_cfg))
                ]
                if inline_items:
                    rows_data.append(inline_items)
            else:
                item_html = cls._render_item(obj, row_config)
                if item_html:
                    rows_data.append({"html": item_html})

        if not rows_data:
            return cfg.get("empty_value", "—")  # type: ignore[return-value]

        return cls.render(rows_data, cfg)

    @classmethod
    def _render_item(cls, obj: Any, item_config: Dict[str, Any]) -> str:
        """Render a single item, dispatching to the appropriate renderer."""
        try:
            field_name = item_config.get("field", "")
            widget_type = item_config.get("widget", "text")

            value = cls._get_nested_value(obj, field_name)

            if item_config.get("hide_if_empty", True) and cls._is_empty(value):
                return ""

            if widget_type == "badge":
                return render_badge(value, item_config)
            if widget_type == "datetime_relative":
                return render_datetime(value, item_config)
            if widget_type == "money_field":
                return render_money(obj, field_name, item_config)
            return render_text(value, item_config)

        except Exception:
            return ""

    @classmethod
    def _get_nested_value(cls, obj: Any, field_name: str) -> Any:
        """Get value from possibly nested field (e.g., 'brand__name')."""
        parts = field_name.split("__")
        value = obj
        for part in parts:
            if value is None:
                return None
            value = getattr(value, part, None)
        return value

    @classmethod
    def _is_empty(cls, value: Any) -> bool:
        """Check if value is considered empty."""
        if value is None:
            return True
        if isinstance(value, str) and not value.strip():
            return True
        return False
