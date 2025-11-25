"""
Image preview display utility.

Renders clickable image thumbnails that open a global modal.
The modal is shared across all images on the page.
"""

import re
from typing import Any, Dict, Optional

from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


class ImagePreviewDisplay:
    """
    Display utility for image preview with modal zoom and pan.

    Uses a lightweight thumbnail that dispatches event to global modal.
    The global modal (image_preview_modal.html) should be included ONCE
    in the base admin template.

    Usage in admin:
        ImagePreviewField(
            name="photo",
            thumbnail_max_width="150px",
            zoom_enabled=True,
        )
    """

    @classmethod
    def render(
        cls,
        image_url: Optional[str],
        config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Render image thumbnail (opens global modal on click).

        Args:
            image_url: URL of the image
            config: Configuration options

        Returns:
            HTML string with image thumbnail
        """
        if not image_url:
            empty_value = config.get('empty_value', "—") if config else "—"
            return empty_value

        config = config or {}

        context = {
            'image_url': image_url,
            'thumbnail_max_width': config.get('thumbnail_max_width', '200px'),
            'thumbnail_max_height': config.get('thumbnail_max_height', '150px'),
            'border_radius': config.get('border_radius', '8px'),
            'show_info': config.get('show_info', True),
            'zoom_enabled': config.get('zoom_enabled', True),
            'zoom_min': config.get('zoom_min', 0.5),
            'zoom_max': config.get('zoom_max', 5.0),
            'zoom_step': config.get('zoom_step', 0.1),
            'alt_text': config.get('alt_text', 'Image'),
            'caption': config.get('caption_text'),
        }

        return render_to_string(
            'django_admin/widgets/image_preview_thumbnail.html',
            context
        )

    @classmethod
    def render_card(
        cls,
        image_url: Optional[str],
        config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Render image preview card with file info (for change form).

        Args:
            image_url: URL of the image
            config: Configuration options including file_size, dimensions, filename

        Returns:
            HTML string with image card
        """
        if not image_url:
            empty_value = config.get('empty_value', "—") if config else "—"
            return empty_value

        config = config or {}

        # Extract filename from URL if not provided
        filename = config.get('filename')
        if not filename and image_url:
            parts = image_url.split('/')
            filename = parts[-1].split('?')[0] if parts else None
            if filename:
                try:
                    from urllib.parse import unquote
                    filename = unquote(filename)
                except:
                    pass

        # Determine file type from extension
        file_type = config.get('file_type')
        if not file_type and filename:
            ext = filename.rsplit('.', 1)[-1].upper() if '.' in filename else None
            if ext in ('JPG', 'JPEG', 'PNG', 'GIF', 'WEBP', 'SVG', 'BMP', 'AVIF', 'ICO'):
                file_type = 'JPEG' if ext == 'JPG' else ext

        context = {
            'image_url': image_url,
            'thumbnail_width': config.get('thumbnail_width', '120px'),
            'thumbnail_height': config.get('thumbnail_height', '120px'),
            'show_info': config.get('show_info', True),
            'zoom_enabled': config.get('zoom_enabled', True),
            'zoom_min': config.get('zoom_min', 0.5),
            'zoom_max': config.get('zoom_max', 5.0),
            'zoom_step': config.get('zoom_step', 0.1),
            'alt_text': config.get('alt_text', 'Image'),
            'filename': filename,
            'file_size': config.get('file_size'),
            'dimensions': config.get('dimensions'),
            'file_type': file_type,
        }

        return render_to_string(
            'django_admin/widgets/image_preview_card.html',
            context
        )

    @classmethod
    def render_modal(cls) -> str:
        """
        Render global modal component.

        Call this ONCE in base admin template to enable
        image preview functionality across all pages.

        Returns:
            HTML string with global modal component
        """
        return render_to_string('django_admin/widgets/image_preview_modal.html')

    @classmethod
    def from_field(
        cls,
        obj: Any,
        field: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Render image thumbnail from model field.

        Args:
            obj: Model instance
            field: Field name
            config: Configuration options

        Returns:
            HTML string with image thumbnail
        """
        from django.utils.safestring import mark_safe

        config = config or {}

        # Check condition if specified
        condition_field = config.get('condition_field')
        if condition_field:
            condition_value = config.get('condition_value', True)
            actual_value = getattr(obj, condition_field, None)
            if actual_value != condition_value:
                # Condition not met - show fallback
                fallback_text = config.get('fallback_text')
                if fallback_text:
                    variant = config.get('fallback_badge_variant', 'secondary')
                    return mark_safe(
                        f'<span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium '
                        f'bg-base-100 text-base-600 dark:bg-base-800 dark:text-base-400">{fallback_text}</span>'
                    )
                return config.get('empty_value', "—")

        # Get image URL - support url_method, direct fields, and methods
        url_method = config.get('url_method')
        if url_method:
            method = getattr(obj, url_method, None)
            image_url = method() if callable(method) else None
        else:
            value = getattr(obj, field, None)
            if callable(value):
                image_url = value()
            elif value and hasattr(value, 'url'):
                # Django ImageField/FileField
                image_url = value.url
            else:
                image_url = value

        if not image_url:
            fallback_text = config.get('fallback_text')
            if fallback_text:
                return mark_safe(
                    f'<span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium '
                    f'bg-base-100 text-base-600 dark:bg-base-800 dark:text-base-400">{fallback_text}</span>'
                )
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
