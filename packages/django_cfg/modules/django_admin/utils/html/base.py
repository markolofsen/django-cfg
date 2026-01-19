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

        # Unfold-compatible Tailwind text colors
        if variant:
            variant_classes = {
                'success': 'text-green-700 dark:text-green-400',
                'warning': 'text-orange-700 dark:text-orange-400',
                'danger': 'text-red-700 dark:text-red-400',
                'info': 'text-blue-700 dark:text-blue-400',
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
    def link(
        url: str,
        text: str,
        css_class: str = "",
        target: str = "",
        icon: Optional[str] = None,
        variant: Optional[str] = None
    ) -> SafeString:
        """
        Render link.

        Args:
            url: URL
            text: Link text
            css_class: CSS classes
            target: Target attribute (_blank, _self, etc)
            icon: Icon name from Icons class
            variant: Color variant
        """
        classes = []
        if css_class:
            classes.append(css_class)
            
        if variant:
            # Unfold-compatible Tailwind text colors for links
            variant_classes = {
                'success': 'text-green-700 dark:text-green-400 hover:text-green-800',
                'warning': 'text-orange-700 dark:text-orange-400 hover:text-orange-800',
                'danger': 'text-red-700 dark:text-red-400 hover:text-red-800',
                'info': 'text-blue-700 dark:text-blue-400 hover:text-blue-800',
                'primary': 'text-primary-600 dark:text-primary-400 hover:text-primary-700',
            }
            classes.append(variant_classes.get(variant, ''))

        final_css_class = " ".join(classes)
        
        content = escape(text)
        if icon:
            # Use BaseElements.icon directly
            icon_html = BaseElements.icon(icon, size="sm", css_class="mr-1 align-text-bottom")
            content = format_html("{} {}", icon_html, content)

        if target:
            return format_html(
                '<a href="{}" class="{}" target="{}">{}</a>',
                url, final_css_class, target, content
            )
        return format_html('<a href="{}" class="{}">{}</a>', url, final_css_class, content)

    @staticmethod
    def empty(text: str = "—") -> SafeString:
        """Render empty/placeholder value."""
        return format_html(
            '<span class="text-font-subtle-light dark:text-font-subtle-dark">{}</span>',
            escape(text)
        )
