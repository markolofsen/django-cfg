"""
Status badges display utility.

Renders multiple conditional status badges.
"""

from typing import Any, Dict, List, Optional

from django.template.loader import render_to_string
from django.utils.html import format_html
from django.utils.safestring import SafeString

from ..html import _classes as C


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
    ) -> SafeString:
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
            'empty_color_class': C.badge(config.get('empty_variant', 'secondary'), default='neutral'),
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
    ) -> SafeString:
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
            return format_html(
                '<span class="cfg-danger cfg-strong">StatusBadgesField Error: Field "{}" not found</span>',
                field,
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
                    'color_class': C.badge(variant, default='neutral'),
                    'icon': icon,
                })

        return cls.render(badges, config)
