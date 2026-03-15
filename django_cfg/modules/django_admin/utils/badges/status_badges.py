"""
Badge utilities with Material Icons.
"""

import logging
from typing import Optional, Union

from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.html import escape, format_html
from django.utils.safestring import SafeString

from ...icons import Icons
from ...models.badge_models import StatusBadgeConfig
from ...models.base import BadgeVariant

logger = logging.getLogger(__name__)


class StatusBadge:
    """Status badge utilities."""

    # Status mappings
    STATUS_MAPPINGS = {
        'active': BadgeVariant.SUCCESS,
        'success': BadgeVariant.SUCCESS,
        'completed': BadgeVariant.SUCCESS,
        'pending': BadgeVariant.WARNING,
        'processing': BadgeVariant.WARNING,
        'failed': BadgeVariant.DANGER,
        'error': BadgeVariant.DANGER,
        'cancelled': BadgeVariant.DANGER,
        'inactive': BadgeVariant.SECONDARY,
    }

    # Unfold-compatible Tailwind CSS classes
    VARIANT_CLASSES = {
        BadgeVariant.SUCCESS: 'bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400',
        BadgeVariant.WARNING: 'bg-orange-100 text-orange-700 dark:bg-orange-500/20 dark:text-orange-400',
        BadgeVariant.DANGER: 'bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400',
        BadgeVariant.INFO: 'bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-400',
        BadgeVariant.PRIMARY: 'bg-primary-100 text-primary-700 dark:bg-primary-500/20 dark:text-primary-400',
        BadgeVariant.SECONDARY: 'bg-base-100 text-base-700 dark:bg-base-500/20 dark:text-base-200',
    }

    @classmethod
    def auto(cls, status: str, config: Optional[StatusBadgeConfig] = None) -> SafeString:
        """Auto status badge with color mapping."""
        config = config or StatusBadgeConfig()

        if status is None or status == '':
            return format_html('<span class="text-font-subtle-light dark:text-font-subtle-dark">—</span>')

        # Normalize status for lookup (handle booleans)
        if isinstance(status, bool):
            lookup_key = 'true' if status else 'false'
            display_text = 'Yes' if status else 'No'
        else:
            lookup_key = str(status)
            display_text = str(status).replace('_', ' ').title()

        # Determine variant
        status_lower = lookup_key.lower().replace('_', '').replace('-', '')
        variant = BadgeVariant.INFO

        for keyword, mapped_variant in cls.STATUS_MAPPINGS.items():
            if keyword in status_lower:
                variant = mapped_variant
                break

        # Use custom mapping if provided
        if config.custom_mappings and lookup_key in config.custom_mappings:
            variant_str = config.custom_mappings[lookup_key]
            try:
                variant = BadgeVariant(variant_str)
            except ValueError:
                pass

        return cls.create(display_text, variant, config)

    @classmethod
    def create(cls, text: str, variant: Union[BadgeVariant, str] = BadgeVariant.INFO,
              config: Optional[StatusBadgeConfig] = None, icon: Optional[str] = None) -> SafeString:
        """Create custom badge."""
        config = config or StatusBadgeConfig()

        if isinstance(variant, str):
            try:
                variant = BadgeVariant(variant)
            except ValueError:
                variant = BadgeVariant.INFO

        css_classes = cls.VARIANT_CLASSES.get(variant, cls.VARIANT_CLASSES[BadgeVariant.INFO])

        if config.css_classes:
            css_classes += ' ' + ' '.join(config.css_classes)

        # Icon with Material Icons integration
        icon_html = ""
        if icon or (config.show_icons and config.icon):
            icon_to_use = icon or config.icon
            if icon_to_use:
                # Use custom icon
                icon_html = format_html('<span class="material-symbols-outlined text-xs mr-1">{}</span>', icon_to_use)
            else:
                # Auto-detect icon based on variant
                icon_map = {
                    BadgeVariant.SUCCESS: Icons.CHECK_CIRCLE,
                    BadgeVariant.WARNING: Icons.WARNING,
                    BadgeVariant.DANGER: Icons.ERROR,
                    BadgeVariant.INFO: Icons.INFO,
                    BadgeVariant.PRIMARY: Icons.STAR,
                    BadgeVariant.SECONDARY: Icons.INFO,
                }
                icon_name = icon_map.get(variant, Icons.INFO)
                icon_html = format_html('<span class="material-symbols-outlined text-xs mr-1">{}</span>', icon_name)

        return format_html(
            '<span class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium {}">'
            '{}{}'
            '</span>',
            css_classes, icon_html, escape(text)
        )


class ProgressBadge:
    """Progress badge utilities."""

    @classmethod
    def percentage(cls, percentage: Union[int, float]) -> SafeString:
        """Progress badge with percentage."""
        percentage = max(0, min(100, float(percentage)))

        if percentage >= 100:
            variant = BadgeVariant.SUCCESS
        elif percentage >= 75:
            variant = BadgeVariant.INFO
        elif percentage >= 50:
            variant = BadgeVariant.WARNING
        else:
            variant = BadgeVariant.SECONDARY

        return StatusBadge.create(f"{percentage:.0f}%", variant)


class CounterBadge:
    """Counter badge utilities."""

    @classmethod
    def simple(cls, count: int, label: str = None, icon: Optional[str] = None,
               variant: Optional[Union[BadgeVariant, str]] = None) -> SafeString:
        """
        Simple counter badge with optional icon.

        Args:
            count: The number to display
            label: Optional label to append (e.g., "links", "items")
            icon: Optional Material Icon name
            variant: Optional variant to override auto color selection
        """
        # Auto-select variant based on count if not provided
        if variant is None:
            if count == 0:
                variant = BadgeVariant.SECONDARY
            elif count < 10:
                variant = BadgeVariant.INFO
            elif count < 100:
                variant = BadgeVariant.WARNING
            else:
                variant = BadgeVariant.SUCCESS

        # Format with humanize for large numbers
        if count >= 1000:
            count_text = intcomma(count)
        else:
            count_text = str(count)

        display_text = f"{count_text} {label}" if label else count_text

        return StatusBadge.create(display_text, variant, icon=icon)
