"""
Badge elements for Django Admin.

Provides badge rendering with variants and icons.
"""

from typing import Any, Optional

from django.utils.html import escape, format_html
from django.utils.safestring import SafeString

from . import _classes as C


class BadgeElements:
    """Badge display elements."""

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
        css_classes = C.badge(variant, default='primary')

        icon_html = ""
        if icon:
            icon_html = format_html('<span class="{}">{}</span>', C.ICON, icon)

        # Check if text is already safe HTML (e.g., from self.html.number() or self.html.inline())
        if isinstance(text, SafeString):
            # Already safe, don't escape
            text_html = text
        else:
            # Regular text, escape for safety
            text_html = escape(str(text))

        return format_html(
            '<span class="{}">{}{}</span>',
            css_classes, icon_html, text_html
        )
