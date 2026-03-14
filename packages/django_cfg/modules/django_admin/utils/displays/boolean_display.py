"""Boolean display utilities."""
from __future__ import annotations

from typing import Optional

from django.utils.html import format_html
from django.utils.safestring import SafeString


class BooleanDisplay:
    """Boolean display utilities."""

    @classmethod
    def icon(
        cls,
        value: bool,
        true_icon: Optional[str] = None,
        false_icon: Optional[str] = None,
    ) -> SafeString:
        """Display boolean as a Material Symbol icon."""
        from ...icons import Icons  # lazy — avoids AppRegistryNotReady

        if value:
            icon = true_icon or Icons.CHECK_CIRCLE
            return format_html(
                '<span class="material-symbols-outlined text-green-600 dark:text-green-400" style="font-size: 20px;">{}</span>',
                icon,
            )
        icon = false_icon or Icons.CANCEL
        return format_html(
            '<span class="material-symbols-outlined text-red-600 dark:text-red-400" style="font-size: 20px;">{}</span>',
            icon,
        )
