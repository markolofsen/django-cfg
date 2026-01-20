"""
Stacked display utility.

Renders multiple field values in a stacked layout.
"""

from typing import Any, Dict, List, Optional, Union

from django.template.loader import render_to_string


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
    ) -> str:
        """
        Render stacked display.

        Args:
            rows_data: List of row data. Each item is either:
                - A dict with 'html' key (single item row)
                - A list of dicts (inline row with multiple items)
            config: Configuration options

        Returns:
            HTML string with stacked layout
        """
        config = config or {}

        context = {
            "rows": rows_data,
            "gap": config.get("gap", "0.25rem"),
            "inline_gap": config.get("inline_gap", "0.5rem"),
            "align": config.get("align", "left"),
            "min_width": config.get("min_width"),
            "max_width": config.get("max_width", "300px"),
        }

        return render_to_string(
            "django_admin/widgets/stacked_display.html", context
        )

    @classmethod
    def from_field(
        cls,
        obj: Any,
        field: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Render stacked display from model object.

        Args:
            obj: Model instance
            field: Virtual field name (not used, rows define actual fields)
            config: Configuration with 'rows' defining the layout

        Returns:
            HTML string with stacked layout
        """
        config = config or {}
        rows_config = config.get("rows", [])

        if not rows_config:
            return config.get("empty_value", "—")

        # Build row data
        rows_data = []

        for row_config in rows_config:
            if isinstance(row_config, list):
                # Inline row with multiple items
                inline_items = []
                for item_config in row_config:
                    item_html = cls._render_item(obj, item_config)
                    if item_html:  # Only add if not empty
                        inline_items.append({"html": item_html})
                if inline_items:
                    rows_data.append(inline_items)
            else:
                # Single item row
                item_html = cls._render_item(obj, row_config)
                if item_html:  # Only add if not empty
                    rows_data.append({"html": item_html})

        if not rows_data:
            return config.get("empty_value", "—")

        return cls.render(rows_data, config)

    @classmethod
    def _render_item(cls, obj: Any, item_config: Dict[str, Any]) -> str:
        """
        Render a single item.

        Args:
            obj: Model instance
            item_config: Item configuration

        Returns:
            HTML string for the item, or empty string if should be hidden
        """
        try:
            field_name = item_config.get("field", "")
            widget_type = item_config.get("widget", "text")

            # Get field value
            value = cls._get_nested_value(obj, field_name)

            # Check if should hide empty
            hide_if_empty = item_config.get("hide_if_empty", True)
            if hide_if_empty and cls._is_empty(value):
                return ""

            # Build item HTML based on widget type
            if widget_type == "badge":
                return cls._render_badge(value, item_config)
            elif widget_type == "datetime_relative":
                return cls._render_datetime(value, item_config)
            elif widget_type == "money_field":
                return cls._render_money(obj, field_name, item_config)
            else:
                # Default to text
                return cls._render_text(value, item_config)
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

    @classmethod
    def _render_text(cls, value: Any, config: Dict[str, Any]) -> str:
        """Render text item."""
        if value is None:
            value = ""
        else:
            value = str(value)

        # Truncate if needed
        truncate = config.get("truncate")
        full_value = value
        if truncate and len(value) > truncate:
            value = value[:truncate] + "…"

        # Apply prefix/suffix (handle None values)
        prefix = config.get("prefix") or ""
        suffix = config.get("suffix") or ""
        text = f"{prefix}{value}{suffix}"

        # Build CSS classes
        classes = ["text-sm"]
        if config.get("bold"):
            classes.append("font-semibold")
        if config.get("muted"):
            classes.append("text-font-subtle-light dark:text-font-subtle-dark")
        if config.get("monospace"):
            classes.append("font-mono")

        # Icon
        icon_html = ""
        if config.get("icon"):
            icon_html = (
                f'<span class="material-symbols-outlined text-sm mr-1">'
                f'{config["icon"]}</span>'
            )

        # Tooltip for truncated text
        tooltip = ""
        if truncate and len(full_value) > truncate:
            tooltip = f'title="{full_value}"'

        return (
            f'<span class="{" ".join(classes)}" {tooltip}>'
            f"{icon_html}{text}</span>"
        )

    @classmethod
    def _render_badge(cls, value: Any, config: Dict[str, Any]) -> str:
        """Render badge item."""
        if value is None:
            return ""

        # Handle boolean values with custom labels
        if isinstance(value, bool):
            if value:
                true_label = config.get("true_label")
                if true_label:
                    value_str = true_label
                else:
                    return ""  # Hide True without label
            else:
                false_label = config.get("false_label")
                if false_label:
                    value_str = false_label
                else:
                    return ""  # Hide False without label
        else:
            value_str = str(value)

        # Determine variant
        variant = config.get("variant", "secondary")
        label_map = config.get("label_map", {})
        if value in label_map:
            variant = label_map[value]
        elif value_str.lower() in label_map:
            variant = label_map[value_str.lower()]

        # Badge color classes (matching Unfold/badges.py style)
        color_classes = {
            "primary": "bg-primary-100 text-primary-700 dark:bg-primary-500/20 dark:text-primary-400",
            "secondary": "bg-base-100 text-base-700 dark:bg-base-500/20 dark:text-base-200",
            "success": "bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400",
            "danger": "bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400",
            "warning": "bg-yellow-100 text-yellow-700 dark:bg-yellow-500/20 dark:text-yellow-400",
            "info": "bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-400",
        }
        color = color_classes.get(variant, color_classes["secondary"])

        # Icon
        icon_html = ""
        if config.get("icon"):
            icon_html = (
                f'<span class="material-symbols-outlined text-xs mr-0.5">'
                f'{config["icon"]}</span>'
            )

        return (
            f'<span class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs '
            f'font-medium {color}">{icon_html}{value_str}</span>'
        )

    @classmethod
    def _render_datetime(cls, value: Any, config: Dict[str, Any]) -> str:
        """Render datetime item."""
        if value is None:
            return ""

        from django.utils import timezone
        from django.utils.timesince import timesince

        # Build CSS classes
        classes = ["text-xs"]
        if config.get("muted", True):
            classes.append("text-font-subtle-light dark:text-font-subtle-dark")

        if config.get("show_relative", False):
            # Show relative time
            try:
                relative = timesince(value, timezone.now())
                text = f"{relative} ago"
            except Exception:
                text = str(value)
        else:
            # Show formatted date
            try:
                text = value.strftime("%Y-%m-%d %H:%M")
            except Exception:
                text = str(value)

        return f'<span class="{" ".join(classes)}">{text}</span>'

    @classmethod
    def _render_money(
        cls, obj: Any, field_name: str, config: Dict[str, Any]
    ) -> str:
        """Render money field item."""
        # Try to use full_display property if available
        full_display_field = f"{field_name}_full_display"
        if hasattr(obj, full_display_field):
            value = getattr(obj, full_display_field)
            if value:
                classes = ["text-sm font-medium"]
                return f'<span class="{" ".join(classes)}">{value}</span>'

        # Fallback to raw value
        value = getattr(obj, field_name, None)
        if value is None:
            return ""

        classes = ["text-sm font-medium"]
        return f'<span class="{" ".join(classes)}">{value:,.2f}</span>'
