"""
Key-value display elements for Django Admin.

Provides utilities for displaying key-value pairs, breakdowns, and lists.
"""

from typing import Any, List, Optional

from django.utils.html import escape, format_html
from django.utils.safestring import SafeString, mark_safe

from . import _classes as C


class KeyValueElements:
    """Key-value display utilities."""

    @staticmethod
    def icon(icon_name: str, size: str = "xs") -> SafeString:
        """Helper to get icon (internal use)."""
        from .base import BaseElements
        return BaseElements.icon(icon_name, size)

    @staticmethod
    def text(content: Any, variant: Optional[str] = None, size: Optional[str] = None) -> SafeString:
        """Helper to get styled text (internal use)."""
        from .base import BaseElements
        return BaseElements.text(content, variant=variant, size=size)

    @staticmethod
    def key_value(
        key: str,
        value: Any,
        icon: Optional[str] = None,
        indent: bool = False,
        divider: bool = False,
        value_variant: Optional[str] = None,
        value_size: Optional[str] = None
    ) -> SafeString:
        """
        Render single key-value pair.

        Args:
            key: Key text
            value: Value (can be SafeString from other html methods)
            icon: Material icon name
            indent: Indent the item
            divider: Show divider above
            value_variant: Color variant for value ('success', 'warning', etc)
            value_size: Size for value ('sm', 'base', 'lg')

        Usage:
            html.key_value('Total', '100 BTC')
            html.key_value('Available', '60 BTC', icon=Icons.CHECK_CIRCLE, indent=True)
            html.key_value('Price', '$1,234', divider=True, value_variant='success', value_size='lg')

        Returns:
            SafeString with key-value HTML
        """
        classes = [C.KV]
        if indent:
            classes.append("cfg-kv-indent")
        if divider:
            classes.append("cfg-kv-divider")

        # Wrap value if variant or size specified
        if value_variant or value_size:
            value = KeyValueElements.text(value, variant=value_variant, size=value_size)

        icon_html = KeyValueElements.icon(icon, size="xs") if icon else ""

        return format_html(
            '<dl class="{}"><dt>{}{}</dt><dd>{}</dd></dl>',
            C.join(*classes), icon_html, key, value,
        )

    @staticmethod
    def divider(css_class: str = "") -> SafeString:
        """
        Render horizontal divider line.

        Args:
            css_class: CSS classes for the hr element

        Usage:
            html.breakdown(
                section1,
                html.divider(),
                section2,
            )

        Returns:
            SafeString with hr element
        """
        if css_class:
            return format_html('<hr class="{}">', css_class)
        return mark_safe('<hr>')

    @staticmethod
    def breakdown(*items: SafeString) -> SafeString:
        """
        Combine multiple key-value pairs into a breakdown section.

        Args:
            *items: Variable number of SafeStrings (from html.key_value())

        Usage:
            html.breakdown(
                html.key_value('Total', total_val),
                html.key_value('Available', avail_val, icon=Icons.CHECK_CIRCLE, indent=True),
                html.key_value('Locked', locked_val, icon=Icons.LOCK, indent=True),
                html.key_value('Price', price, divider=True) if has_price else None,
                html.key_value('Total Value', usd_val, value_variant='success', value_size='lg') if has_price else None,
            )

        Returns:
            SafeString with combined breakdown HTML
        """
        # Filter out None values
        filtered = [str(item) for item in items if item is not None]

        return format_html('<div class="{}">{}</div>', C.STACK, mark_safe(''.join(filtered)))

    @staticmethod
    def key_value_list(
        items: List[dict],
        layout: str = "vertical",
        key_width: Optional[str] = None,
        spacing: str = "normal"
    ) -> SafeString:
        """
        Render key-value pairs as a formatted list.

        Args:
            items: List of dicts with 'key', 'value', and optional keys:
                - icon: Material icon name
                - indent: Boolean for indentation
                - value_class: extra CSS classes for the value (cfg-success, ...)
                - divider: Boolean to show divider above
                - size: 'sm', 'base', 'lg'
            layout: "vertical" or "horizontal"
            key_width: Fixed width for keys (e.g., "100px") for alignment
            spacing: "tight", "normal", "relaxed"

        Usage:
            # Simple key-value list
            html.key_value_list([
                {'key': 'Total', 'value': '100 BTC', 'size': 'lg'},
                {'key': 'Available', 'value': '60 BTC', 'indent': True},
                {'key': 'Locked', 'value': '40 BTC', 'indent': True},
            ])

            # With icons and styling
            html.key_value_list([
                {'key': 'Available', 'value': '60 BTC', 'icon': Icons.CHECK_CIRCLE},
                {'key': 'Total Value', 'value': '$1,234.56', 'value_class': 'cfg-success', 'divider': True},
            ])

        Returns:
            SafeString with formatted key-value list HTML
        """
        parts = []
        for item in items:
            row_classes = C.join(
                "cfg-kv-indent" if item.get('indent') else "",
                "cfg-kv-divider" if item.get('divider') else "",
            )
            icon = item.get('icon', '')
            icon_html = KeyValueElements.icon(icon, size="xs") if icon else ""
            parts.append(format_html(
                '<dt class="{}">{}{}</dt><dd class="{}">{}</dd>',
                row_classes,
                icon_html,
                item.get('key', ''),
                C.join(row_classes, item.get('value_class', ''), C.SMALL if item.get('size') == 'sm' else ''),
                item.get('value', ''),  # SafeString from html.number() stays unescaped
            ))

        css = C.join(C.KV, "cfg-kv-tight" if spacing == "tight" else "")
        return format_html('<dl class="{}">{}</dl>', css, mark_safe(''.join(str(p) for p in parts)))
