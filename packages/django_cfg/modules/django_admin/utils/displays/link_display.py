"""
Link display utility.

Renders text with link and optional subtitle.
"""

import re
from typing import Any, Dict, Optional

from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


class LinkDisplay:
    """
    Display utility for links with subtitle.

    Usage in admin:
        LinkField(
            name="title",
            link_field="url",
            subtitle_field="description",
        )
    """

    @classmethod
    def render(
        cls,
        text: str,
        link_url: Optional[str],
        config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Render link with optional subtitle.

        Args:
            text: Display text
            link_url: URL to link to
            config: Configuration options

        Returns:
            HTML string with link
        """
        config = config or {}

        if not link_url:
            return str(text)

        context = {
            'text': text,
            'link_url': link_url,
            'link_icon': config.get('link_icon'),
            'link_target': config.get('link_target', '_blank'),
            'subtitle_text': config.get('subtitle_text'),
            'subtitle_css_class': config.get('subtitle_css_class', 'text-sm text-gray-500'),
        }

        return render_to_string(
            'django_admin/widgets/link_display.html',
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
        Render link from model field.

        Args:
            obj: Model instance
            field: Field name for text
            config: Configuration options

        Returns:
            HTML string with link
        """
        config = config or {}

        # Validate field exists
        if not hasattr(obj, field):
            return mark_safe(
                f'<span class="text-red-600 font-bold">'
                f'LinkField Error: Field "{field}" not found</span>'
            )

        # Get field values
        text = getattr(obj, field, '')
        link_field = config.get('link_field')
        link_url = getattr(obj, link_field, '') if link_field else ''

        if not link_url:
            return str(text)

        # Build subtitle
        subtitle_text = None
        subtitle_template = config.get('subtitle_template')
        subtitle_fields = config.get('subtitle_fields')
        subtitle_field = config.get('subtitle_field')
        subtitle_separator = config.get('subtitle_separator', ' • ')

        if subtitle_template:
            # Template with {field_name} placeholders
            template = subtitle_template
            field_names = re.findall(r'\{(\w+)\}', template)
            for field_name in field_names:
                field_value = getattr(obj, field_name, '')
                template = template.replace(f'{{{field_name}}}', str(field_value))
            subtitle_text = template
        elif subtitle_fields:
            # Multiple fields with separator
            parts = [
                str(getattr(obj, f, ''))
                for f in subtitle_fields
                if getattr(obj, f, '')
            ]
            subtitle_text = subtitle_separator.join(parts) if parts else None
        elif subtitle_field:
            # Single field
            subtitle_text = str(getattr(obj, subtitle_field, ''))

        # Build config for render
        render_config = {
            'link_icon': config.get('link_icon'),
            'link_target': config.get('link_target', '_blank'),
            'subtitle_text': subtitle_text,
            'subtitle_css_class': config.get('subtitle_css_class', 'text-sm text-gray-500'),
        }

        return cls.render(text, link_url, render_config)
