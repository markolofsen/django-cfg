"""
Status badges display utility.

Renders multiple conditional status badges.
"""

from typing import Any, Dict, List, Optional

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


class StatusBadgesDisplay:
    """
    Display utility for multiple conditional status badges.

    Usage in admin:
        StatusBadgesField(
            name="status",
            badge_rules=[
                BadgeRule(condition_field="is_active", label="Active", variant="success"),
                BadgeRule(condition_field="is_verified", label="Verified", variant="info"),
            ]
        )
    """

    @classmethod
    def render(
        cls,
        badges: List[Dict[str, Any]],
        config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Render multiple status badges.

        Args:
            badges: List of badge dicts with label, color_class, icon
            config: Configuration options

        Returns:
            HTML string with badges
        """
        config = config or {}

        context = {
            'badges': badges,
            'separator': config.get('separator', ' '),
            'empty_text': config.get('empty_text'),
            'empty_color_class': BADGE_COLORS.get(
                config.get('empty_variant', 'secondary'),
                BADGE_COLORS['secondary']
            ),
        }

        return render_to_string(
            'django_admin/widgets/status_badges_display.html',
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
        Render status badges from model field.

        Args:
            obj: Model instance
            field: Field name (used for validation)
            config: Configuration options

        Returns:
            HTML string with badges
        """
        config = config or {}

        # Validate field exists
        if not hasattr(obj, field):
            return mark_safe(
                f'<span class="text-red-600 font-bold">'
                f'StatusBadgesField Error: Field "{field}" not found</span>'
            )

        badge_rules = config.get('badge_rules', [])

        # Check each rule and collect matching badges
        badges = []
        for rule in badge_rules:
            condition_field = rule.get('condition_field')
            condition_value = rule.get('condition_value', True)
            label = rule.get('label', '')
            variant = rule.get('variant', 'secondary')
            icon = rule.get('icon')

            # Check if condition matches
            field_value = getattr(obj, condition_field, None)
            if field_value == condition_value:
                badges.append({
                    'label': label,
                    'color_class': BADGE_COLORS.get(variant, BADGE_COLORS['secondary']),
                    'icon': icon,
                })

        return cls.render(badges, config)
