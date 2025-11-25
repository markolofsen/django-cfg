"""
Avatar display utility.

Renders user avatar with fallback to initials badge.
"""

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


class AvatarDisplay:
    """
    Display utility for avatar with initials fallback.

    Usage in admin:
        AvatarField(
            name="user",
            photo_field="avatar",
            name_field="full_name",
            initials_field="full_name",
        )
    """

    @classmethod
    def render(
        cls,
        photo_url: Optional[str],
        name: str,
        initials: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Render avatar with initials fallback.

        Args:
            photo_url: URL of the avatar image (or None)
            name: Display name
            initials: Initials to show if no photo
            config: Configuration options

        Returns:
            HTML string with avatar
        """
        config = config or {}

        avatar_size = config.get('avatar_size', 40)
        show_as_card = config.get('show_as_card', False)
        subtitle = config.get('subtitle')
        variant = config.get('variant', 'secondary')

        color_class = BADGE_COLORS.get(variant, BADGE_COLORS['secondary'])

        context = {
            'photo_url': photo_url,
            'name': name,
            'initials': initials,
            'avatar_size': avatar_size,
            'show_as_card': show_as_card,
            'subtitle': subtitle,
            'color_class': color_class,
        }

        return render_to_string(
            'django_admin/widgets/avatar_display.html',
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
        Render avatar from model field.

        Args:
            obj: Model instance
            field: Field name (used for validation)
            config: Configuration options

        Returns:
            HTML string with avatar
        """
        config = config or {}

        # Validate field exists
        if not hasattr(obj, field):
            return mark_safe(
                f'<span class="text-red-600 font-bold">'
                f'AvatarField Error: Field "{field}" not found</span>'
            )

        # Get configuration
        photo_field = config.get('photo_field')
        name_field = config.get('name_field')
        initials_field = config.get('initials_field')
        subtitle_field = config.get('subtitle_field')

        # Validate required fields
        if not photo_field or not name_field or not initials_field:
            return mark_safe(
                '<span class="text-gray-500">'
                'Avatar config missing (photo_field, name_field, initials_field required)'
                '</span>'
            )

        # Get field values
        photo = getattr(obj, photo_field, None) if photo_field else None
        name = str(getattr(obj, name_field, '')) if name_field else ''
        initials_source = str(getattr(obj, initials_field, '')) if initials_field else ''
        subtitle = str(getattr(obj, subtitle_field, '')) if subtitle_field else None

        # Extract photo URL
        photo_url = None
        if photo:
            photo_url = photo.url if hasattr(photo, 'url') else str(photo)

        # Extract initials
        initials_max_length = config.get('initials_max_length', 2)
        initials = ''.join([
            word[0].upper()
            for word in str(initials_source).split()[:initials_max_length]
        ])
        if not initials:
            initials = str(name)[0].upper() if name else '?'

        # Determine variant
        variant = config.get('default_variant', 'secondary')
        variant_field = config.get('variant_field')
        variant_map = config.get('variant_map', {})
        if variant_field:
            variant_value = getattr(obj, variant_field, None)
            variant = variant_map.get(variant_value, variant)

        # Build config for render
        render_config = {
            'avatar_size': config.get('avatar_size', 40),
            'show_as_card': config.get('show_as_card', False),
            'subtitle': subtitle,
            'variant': variant,
        }

        return cls.render(photo_url, name, initials, render_config)
