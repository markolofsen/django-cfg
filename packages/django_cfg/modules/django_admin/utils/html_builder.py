"""
Universal HTML builder for Django Admin display methods.
"""

from typing import Any, List, Optional, Union

from django.utils.html import escape, format_html
from django.utils.safestring import SafeString

from ..icons import Icons


class HtmlBuilder:
    """
    Universal HTML builder with Material Icons support.

    Usage in admin methods:
        def stats(self, obj):
            return self.html.inline([
                self.html.icon_text(Icons.EDIT, obj.posts_count),
                self.html.icon_text(Icons.CHAT, obj.comments_count),
            ])
    """

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
    def icon_text(icon_or_text: Union[str, Any], text: Any = None,
                  icon_size: str = "xs", separator: str = " ") -> SafeString:
        """
        Render icon with text or emoji with text.

        Args:
            icon_or_text: Icon from Icons class, emoji, or text if text param is None
            text: Optional text to display after icon
            icon_size: Icon size (xs, sm, base, lg, xl)
            separator: Separator between icon and text

        Usage:
            html.icon_text(Icons.EDIT, 5)  # Icon with number
            html.icon_text("📝", 5)  # Emoji with number
            html.icon_text("Active")  # Just text
        """
        if text is None:
            # Just text
            return format_html('<span>{}</span>', escape(str(icon_or_text)))

        # Check if it's a Material Icon (from Icons class) or emoji
        icon_str = str(icon_or_text)

        # Detect if it's emoji by checking for non-ASCII characters
        is_emoji = any(ord(c) > 127 for c in icon_str)

        if is_emoji or icon_str in ['📝', '💬', '🛒', '👤', '📧', '🔔', '⚙️', '🔧', '📊', '🎯']:
            # Emoji
            icon_html = escape(icon_str)
        else:
            # Material Icon
            icon_html = HtmlBuilder.icon(icon_str, size=icon_size)

        return format_html('{}{}<span>{}</span>', icon_html, separator, escape(str(text)))

    @staticmethod
    def inline(items: List[Any], separator: str = " | ",
               size: str = "small", css_class: str = "") -> SafeString:
        """
        Render items inline with separator.

        Args:
            items: List of SafeString/str items to join
            separator: Separator between items
            size: small, medium, large
            css_class: Additional CSS classes

        Usage:
            html.inline([
                html.icon_text(Icons.EDIT, 5),
                html.icon_text(Icons.CHAT, 10),
            ])
        """
        if not items:
            return format_html('<span class="text-font-subtle-light dark:text-font-subtle-dark">—</span>')

        size_classes = {
            'small': 'text-xs',
            'medium': 'text-sm',
            'large': 'text-base'
        }
        size_class = size_classes.get(size, 'text-xs')

        classes = size_class
        if css_class:
            classes += f" {css_class}"

        # Join items with separator
        joined = format_html(separator.join(['{}'] * len(items)), *items)

        return format_html('<span class="{}">{}</span>', classes, joined)

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
    def badge(text: Any, variant: str = "primary", icon: Optional[str] = None) -> SafeString:
        """
        Render badge with optional icon.

        Args:
            text: Badge text
            variant: primary, success, warning, danger, info, secondary
            icon: Optional Material Icon

        Usage:
            html.badge("Active", variant="success", icon=Icons.CHECK_CIRCLE)
        """
        variant_classes = {
            'success': 'bg-success-100 text-success-800 dark:bg-success-900 dark:text-success-200',
            'warning': 'bg-warning-100 text-warning-800 dark:bg-warning-900 dark:text-warning-200',
            'danger': 'bg-danger-100 text-danger-800 dark:bg-danger-900 dark:text-danger-200',
            'info': 'bg-info-100 text-info-800 dark:bg-info-900 dark:text-info-200',
            'primary': 'bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200',
            'secondary': 'bg-base-100 text-font-default-light dark:bg-base-800 dark:text-font-default-dark',
        }

        css_classes = variant_classes.get(variant, variant_classes['primary'])

        icon_html = ""
        if icon:
            icon_html = format_html('<span class="material-symbols-outlined text-xs mr-1">{}</span>', icon)

        return format_html(
            '<span class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium {}">{}{}</span>',
            css_classes, icon_html, escape(str(text))
        )

    @staticmethod
    def empty(text: str = "—") -> SafeString:
        """Render empty/placeholder value."""
        return format_html(
            '<span class="text-font-subtle-light dark:text-font-subtle-dark">{}</span>',
            escape(text)
        )
