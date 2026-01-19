"""
Badge elements for Django Admin.

Provides badge rendering with variants and icons.
"""

from typing import Optional

from django.utils.html import escape, format_html
from django.utils.safestring import SafeString


class BadgeElements:
    """Badge display elements."""

    @staticmethod
    def badge(text: any, variant: str = "primary", icon: Optional[str] = None) -> SafeString:
        """
        Render badge with optional icon.

        Args:
            text: Badge text
            variant: primary, success, warning, danger, info, secondary
            icon: Optional Material Icon

        Usage:
            html.badge("Active", variant="success", icon=Icons.CHECK_CIRCLE)
        """
        # Unfold-compatible Tailwind CSS classes
        variant_classes = {
            'success': 'bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400',
            'warning': 'bg-orange-100 text-orange-700 dark:bg-orange-500/20 dark:text-orange-400',
            'danger': 'bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400',
            'info': 'bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-400',
            'primary': 'bg-primary-100 text-primary-700 dark:bg-primary-500/20 dark:text-primary-400',
            'secondary': 'bg-base-100 text-base-700 dark:bg-base-500/20 dark:text-base-200',
        }

        css_classes = variant_classes.get(variant, variant_classes['primary'])

        icon_html = ""
        if icon:
            icon_html = format_html('<span class="material-symbols-outlined text-xs mr-1">{}</span>', icon)

        # Check if text is already safe HTML (e.g., from self.html.number() or self.html.inline())
        if isinstance(text, SafeString):
            # Already safe, don't escape
            text_html = text
        else:
            # Regular text, escape for safety
            text_html = escape(str(text))

        return format_html(
            '<span class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium {}">{}{}</span>',
            css_classes, icon_html, text_html
        )
