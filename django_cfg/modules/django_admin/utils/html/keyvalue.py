"""
Key-value display elements for Django Admin.

Provides utilities for displaying key-value pairs, breakdowns, and lists.
"""

from typing import Any, List, Optional

from django.utils.html import escape, format_html
from django.utils.safestring import SafeString, mark_safe


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
        # Classes
        classes = ['mb-2']
        if indent:
            classes.append('ml-5')
        if divider:
            classes.append('mt-4 pt-2 border-t border-base-200 dark:border-base-700')

        # Wrap value if variant or size specified
        if value_variant or value_size:
            value = KeyValueElements.text(value, variant=value_variant, size=value_size)

        # Build parts
        parts = []
        parts.append(f'<div class="{" ".join(classes)}">')

        # Icon
        if icon:
            parts.append(str(KeyValueElements.icon(icon, size="xs")))
            parts.append(' ')

        # Key
        parts.append(f'<span class="font-semibold text-font-default-light dark:text-font-default-dark">{escape(key)}:</span> ')

        # Value
        parts.append(str(value))

        parts.append('</div>')

        return mark_safe(''.join(parts))

    @staticmethod
    def divider(css_class: str = "my-2") -> SafeString:
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
        return format_html('<hr class="{}">', css_class)

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

        return mark_safe(''.join(filtered))

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
                - value_class: Tailwind classes for value
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
                {'key': 'Total Value', 'value': '$1,234.56', 'value_class': 'text-green-700 text-lg', 'divider': True},
            ])

        Returns:
            SafeString with formatted key-value list HTML
        """
        spacing_map = {
            'tight': 'mb-1',
            'normal': 'mb-2',
            'relaxed': 'mb-3'
        }
        spacing_class = spacing_map.get(spacing, 'mb-2')

        parts = []
        for item in items:
            key = item.get('key', '')
            value = item.get('value', '')
            icon = item.get('icon', '')
            indent = item.get('indent', False)
            value_class = item.get('value_class', '')
            divider = item.get('divider', False)
            size = item.get('size', 'base')

            # Icon HTML
            icon_html = ""
            if icon:
                icon_html = f'{KeyValueElements.icon(icon, size="xs")} '

            # Size classes
            size_map = {
                'sm': 'text-sm',
                'base': 'text-base',
                'lg': 'text-lg'
            }
            size_class = size_map.get(size, 'text-base')

            # Classes
            indent_class = 'ml-5' if indent else ''
            divider_class = 'mt-4 pt-2 border-t border-base-200 dark:border-base-700' if divider else ''

            # Build item HTML
            item_html = format_html(
                '<div class="{} {} {} {}">{}<span class="font-semibold">{}:</span> <span class="{}">{}</span></div>',
                spacing_class,
                indent_class,
                divider_class,
                size_class,
                icon_html,
                escape(key),
                value_class,
                value  # Already SafeString from html.number()
            )
            parts.append(item_html)

        return mark_safe(''.join(str(p) for p in parts))
