"""
Simple image display utility.

Renders image without modal (for basic display).
Use ImagePreviewDisplay for interactive modal version.
"""

import re
from typing import Any, Dict, Optional

from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


class ImageDisplay:
    """
    Display utility for simple image rendering.

    For interactive preview with zoom/pan, use ImagePreviewDisplay instead.

    Usage in admin:
        ImageField(
            name="photo",
            max_width="200px",
            caption_field="title",
        )
    """

    @classmethod
    def render(
        cls,
        image_url: Optional[str],
        config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Render simple image.

        Args:
            image_url: URL of the image
            config: Configuration options

        Returns:
            HTML string with image
        """
        if not image_url:
            empty_value = config.get('empty_value', "—") if config else "—"
            return empty_value

        config = config or {}

        # Build style string
        styles = []
        if config.get('width'):
            styles.append(f"width: {config['width']}")
        if config.get('height'):
            styles.append(f"height: {config['height']}")
        if config.get('max_width'):
            styles.append(f"max-width: {config['max_width']}")
        if config.get('max_height'):
            styles.append(f"max-height: {config['max_height']}")
        if config.get('border_radius'):
            styles.append(f"border-radius: {config['border_radius']}")

        context = {
            'image_url': image_url,
            'alt_text': config.get('alt_text', 'Image'),
            'style': '; '.join(styles) if styles else '',
            'caption': config.get('caption_text'),
        }

        return render_to_string(
            'django_admin/widgets/image_display.html',
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
        Render image from model field.

        Args:
            obj: Model instance
            field: Field name
            config: Configuration options

        Returns:
            HTML string with image
        """
        config = config or {}

        # Get image URL - support both direct fields and methods
        value = getattr(obj, field, None)
        if callable(value):
            image_url = value()
        elif value and hasattr(value, 'url'):
            image_url = value.url
        else:
            image_url = value

        if not image_url:
            return config.get('empty_value', "—")

        # Build caption if specified
        caption_text = None
        if config.get('caption'):
            caption_text = config['caption']
        elif config.get('caption_field'):
            caption_text = str(getattr(obj, config['caption_field'], ''))
        elif config.get('caption_template'):
            template = config['caption_template']
            field_names = re.findall(r'\{(\w+)\}', template)
            for field_name in field_names:
                field_value = getattr(obj, field_name, '')
                template = template.replace(f'{{{field_name}}}', str(field_value))
            caption_text = template

        config['caption_text'] = caption_text

        return cls.render(image_url, config)
