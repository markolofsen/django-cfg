"""
Text display utilities with truncation and styling.
"""

from typing import Any, Dict, Optional

from django.utils.html import escape, format_html
from django.utils.safestring import SafeString


class TextDisplay:
    """Text display with truncation, nowrap, and styling options."""

    @classmethod
    def from_field(cls, obj: Any, field_name: str, config: Dict[str, Any]) -> SafeString:
        """
        Render text field with configuration.

        Config options:
            truncate: int - Max characters to show (default: None = no truncation)
            monospace: bool - Use monospace font (default: False)
            nowrap: bool - Prevent line wrapping (default: True)
            max_width: str - CSS max-width (default: "300px")
            show_tooltip: bool - Show full text on hover (default: True when truncated)
        """
        value = getattr(obj, field_name, None)

        if value is None or value == "":
            return format_html(
                '<span class="text-font-subtle-light dark:text-font-subtle-dark">—</span>'
            )

        text = str(value)
        truncate = config.get('truncate')
        monospace = config.get('monospace', False)
        nowrap = config.get('nowrap', True)
        max_width = config.get('max_width', '300px')
        show_tooltip = config.get('show_tooltip', True)

        # Truncate if needed
        is_truncated = False
        display_text = text
        if truncate and len(text) > truncate:
            display_text = text[:truncate] + "..."
            is_truncated = True

        # Build CSS classes
        classes = ["text-sm"]
        if monospace:
            classes.append("font-mono")

        # Link styling - use primary colors for clickable fields
        is_link = config.get('is_link', False)
        if is_link:
            classes.append("text-primary-600")
            classes.append("dark:text-primary-400")
            classes.append("hover:text-primary-700")
            classes.append("dark:hover:text-primary-500")

        # Build inline styles
        styles = []
        if nowrap:
            styles.append("white-space: nowrap")
            styles.append("overflow: hidden")
            styles.append("text-overflow: ellipsis")
        if max_width:
            styles.append(f"max-width: {max_width}")
        styles.append("display: block")

        class_str = " ".join(classes)
        style_str = "; ".join(styles)

        # Add tooltip for truncated text
        if is_truncated and show_tooltip:
            return format_html(
                '<span class="{}" style="{}" title="{}">{}</span>',
                class_str,
                style_str,
                escape(text),
                escape(display_text)
            )
        else:
            return format_html(
                '<span class="{}" style="{}">{}</span>',
                class_str,
                style_str,
                escape(display_text)
            )

    @classmethod
    def truncated(
        cls,
        text: str,
        max_length: int = 100,
        monospace: bool = False,
        max_width: str = "300px"
    ) -> SafeString:
        """
        Simple truncated text display.

        Args:
            text: Text to display
            max_length: Maximum characters
            monospace: Use monospace font
            max_width: CSS max-width value
        """
        if not text:
            return format_html(
                '<span class="text-font-subtle-light dark:text-font-subtle-dark">—</span>'
            )

        text = str(text)
        is_truncated = len(text) > max_length
        display_text = text[:max_length] + "..." if is_truncated else text

        classes = ["text-sm"]
        if monospace:
            classes.append("font-mono")

        style = f"white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: {max_width}; display: block"

        if is_truncated:
            return format_html(
                '<span class="{}" style="{}" title="{}">{}</span>',
                " ".join(classes),
                style,
                escape(text),
                escape(display_text)
            )
        else:
            return format_html(
                '<span class="{}" style="{}">{}</span>',
                " ".join(classes),
                style,
                escape(display_text)
            )
