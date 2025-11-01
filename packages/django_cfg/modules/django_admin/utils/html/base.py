"""
Basic HTML elements for Django Admin.

Provides fundamental HTML building blocks: icons, spans, text, divs, links, and empty placeholders.
"""

from typing import Any, Optional

from django.utils.html import escape, format_html
from django.utils.safestring import SafeString


class BaseElements:
    """Basic HTML building blocks."""

    @staticmethod
    def icon(icon_name: str, size: str = "xs", css_class: str = "") -> SafeString:
        """
        Render Material Icon.

        Args:
            icon_name: Icon name from Icons class
            size: xs, sm, base, lg, xl
            css_class: Additional CSS classes
        """
        size_classes = {
            'xs': 'text-xs',
            'sm': 'text-sm',
            'base': 'text-base',
            'lg': 'text-lg',
            'xl': 'text-xl'
        }
        size_class = size_classes.get(size, 'text-xs')
        classes = f"material-symbols-outlined {size_class}"
        if css_class:
            classes += f" {css_class}"

        return format_html('<span class="{}">{}</span>', classes, icon_name)

    @staticmethod
    def span(text: Any, css_class: str = "") -> SafeString:
        """
        Render text in span with optional CSS class.

        Args:
            text: Text to display
            css_class: CSS classes
        """
        if css_class:
            return format_html('<span class="{}">{}</span>', css_class, escape(str(text)))
        return format_html('<span>{}</span>', escape(str(text)))

    @staticmethod
    def text(
        content: Any,
        variant: Optional[str] = None,
        size: Optional[str] = None,
        weight: Optional[str] = None,
        muted: bool = False
    ) -> SafeString:
        """
        Render styled text with semantic variants.

        Args:
            content: Text content (can be SafeString from other html methods)
            variant: Color variant - 'success', 'warning', 'danger', 'info', 'primary'
            size: Size - 'xs', 'sm', 'base', 'lg', 'xl', '2xl'
            weight: Font weight - 'normal', 'medium', 'semibold', 'bold'
            muted: Use muted/subtle color

        Usage:
            # Success text
            html.text("$1,234.56", variant="success", size="lg")

            # Muted small text
            html.text("(12.5%)", muted=True, size="sm")

            # Combined with other methods
            total = html.number(1234.56, prefix="$")
            html.text(total, variant="success", size="lg")

        Returns:
            SafeString with styled text
        """
        classes = []

        # Variant colors
        if variant:
            variant_classes = {
                'success': 'text-success-600 dark:text-success-400',
                'warning': 'text-warning-600 dark:text-warning-400',
                'danger': 'text-danger-600 dark:text-danger-400',
                'info': 'text-info-600 dark:text-info-400',
                'primary': 'text-primary-600 dark:text-primary-400',
            }
            classes.append(variant_classes.get(variant, ''))

        # Muted
        if muted:
            classes.append('text-font-subtle-light dark:text-font-subtle-dark')

        # Size
        if size:
            size_classes = {
                'xs': 'text-xs',
                'sm': 'text-sm',
                'base': 'text-base',
                'lg': 'text-lg',
                'xl': 'text-xl',
                '2xl': 'text-2xl',
            }
            classes.append(size_classes.get(size, ''))

        # Weight
        if weight:
            weight_classes = {
                'normal': 'font-normal',
                'medium': 'font-medium',
                'semibold': 'font-semibold',
                'bold': 'font-bold',
            }
            classes.append(weight_classes.get(weight, ''))

        css_class = ' '.join(filter(None, classes))

        if css_class:
            return format_html('<span class="{}">{}</span>', css_class, content)
        return format_html('<span>{}</span>', content)

    @staticmethod
    def div(content: Any, css_class: str = "") -> SafeString:
        """
        Render content in div with optional CSS class.

        Args:
            content: Content to display (can be SafeString)
            css_class: CSS classes
        """
        if css_class:
            return format_html('<div class="{}">{}</div>', css_class, content)
        return format_html('<div>{}</div>', content)

    @staticmethod
    def link(url: str, text: str, css_class: str = "", target: str = "") -> SafeString:
        """
        Render link.

        Args:
            url: URL
            text: Link text
            css_class: CSS classes
            target: Target attribute (_blank, _self, etc)
        """
        if target:
            return format_html(
                '<a href="{}" class="{}" target="{}">{}</a>',
                url, css_class, target, escape(text)
            )
        return format_html('<a href="{}" class="{}">{}</a>', url, css_class, escape(text))

    @staticmethod
    def empty(text: str = "—") -> SafeString:
        """Render empty/placeholder value."""
        return format_html(
            '<span class="text-font-subtle-light dark:text-font-subtle-dark">{}</span>',
            escape(text)
        )
