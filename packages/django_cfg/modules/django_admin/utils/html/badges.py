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
