"""
Counter badge display utility.

Renders counter with optional link.
"""

import re
from typing import Any, Dict, Optional

from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


# Badge color classes mapping
BADGE_COLORS = {
    'primary': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
    'secondary': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
    'success': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
    'danger': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
    'warning': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
    'info': 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900 dark:text-cyan-300',
}


class CounterBadgeDisplay:
    """
    Display utility for counter badge with optional link.

    Usage in admin:
        CounterBadgeField(
            name="comments",
            count_field="comment_count",
            link_url_template="/admin/app/comment/?post__id={obj.id}",
        )
    """

    @classmethod
    def render(
        cls,
        count: int,
        config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Render counter badge.

        Args:
            count: Counter value
            config: Configuration options

        Returns:
            HTML string with counter badge
        """
        config = config or {}

        variant = config.get('variant', 'primary')
        icon = config.get('icon')
        link_url = config.get('link_url')
        link_target = config.get('link_target', '_self')
        format_thousands = config.get('format_thousands', True)
        hide_on_zero = config.get('hide_on_zero', False)
        empty_display = config.get('empty_display', False)
        empty_text = config.get('empty_text', '-')

        # Handle zero count
        if count == 0:
            if hide_on_zero:
                return ""
            count_display = empty_text if empty_display else "0"
        else:
            count_display = f"{count:,}" if format_thousands else str(count)

        context = {
            'count': count,
            'count_display': count_display,
            'color_class': BADGE_COLORS.get(variant, BADGE_COLORS['primary']),
            'icon': icon,
            'link_url': link_url if count > 0 else None,
            'link_target': link_target,
            'hide_on_zero': hide_on_zero,
        }

        return render_to_string(
            'django_admin/widgets/counter_badge_display.html',
            context
        )

    @classmethod
    def from_field(
        cls,
        obj: Any,
        field: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Render counter badge from model field.

        Args:
            obj: Model instance
            field: Field name (used for validation)
            config: Configuration options

        Returns:
            HTML string with counter badge
        """
        config = config or {}

        # Validate field exists
        if not hasattr(obj, field):
            return mark_safe(
                f'<span class="text-red-600 font-bold">'
                f'CounterBadgeField Error: Field "{field}" not found</span>'
            )

        count_field = config.get('count_field')
        count = getattr(obj, count_field, 0) if count_field else 0

        # Process link URL template
        link_url = None
        link_url_template = config.get('link_url_template')
        if link_url_template and count > 0:
            link_url = link_url_template
            placeholders = re.findall(r'\{obj\.(\w+)\}', link_url)
            for placeholder in placeholders:
                value = getattr(obj, placeholder, '')
                link_url = link_url.replace(f'{{obj.{placeholder}}}', str(value))

        render_config = {
            'variant': config.get('variant', 'primary'),
            'icon': config.get('icon'),
            'link_url': link_url,
            'link_target': config.get('link_target', '_self'),
            'format_thousands': config.get('format_thousands', True),
            'hide_on_zero': config.get('hide_on_zero', False),
            'empty_display': config.get('empty_display', False),
            'empty_text': config.get('empty_text', '-'),
        }

        return cls.render(count, render_config)
