"""
Short UUID display utility.

Renders truncated UUID with tooltip and copy-on-click.
"""

from typing import Any, Dict, Optional

from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


class ShortUUIDDisplay:
    """
    Display utility for shortened UUID.

    Usage in admin:
        ShortUUIDField(
            name="id",
            length=8,
            show_full_on_hover=True,
            copy_on_click=True,
        )
    """

    @classmethod
    def render(
        cls,
        uuid_value: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Render shortened UUID.

        Args:
            uuid_value: Full UUID string
            config: Configuration options

        Returns:
            HTML string with shortened UUID
        """
        config = config or {}

        if not uuid_value:
            return config.get('empty_value', "—")

        # Convert to string and remove dashes
        uuid_str = str(uuid_value).replace('-', '')

        # Get configuration
        length = config.get('length', 8)
        show_full_on_hover = config.get('show_full_on_hover', True)
        copy_on_click = config.get('copy_on_click', True)
        is_link = config.get('is_link', False)

        # Truncate
        short_uuid = uuid_str[:length]

        context = {
            'short_uuid': short_uuid,
            'full_uuid': uuid_value,
            'show_full_on_hover': show_full_on_hover,
            'copy_on_click': copy_on_click,
            'is_link': is_link,
        }

        return render_to_string(
            'django_admin/widgets/short_uuid_display.html',
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
        Render short UUID from model field.

        Args:
            obj: Model instance
            field: Field name
            config: Configuration options

        Returns:
            HTML string with shortened UUID
        """
        config = config or {}

        uuid_value = getattr(obj, field, None)

        if not uuid_value:
            return config.get('empty_value', "—")

        return cls.render(uuid_value, config)
