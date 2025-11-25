"""
Image preview widget with modal zoom and pan functionality.

Provides interactive image preview with:
- Click to open in modal
- Scroll zoom with mouse wheel
- Pan/drag image
- Image info display (dimensions, size, format)
- Tailwind 4 + Alpine.js implementation
"""

from typing import Any, Optional

from django import forms


class ImagePreviewWidget(forms.ClearableFileInput):
    """
    Image preview widget with modal zoom and pan.

    Features:
    - Thumbnail preview in form
    - Click to open fullscreen modal
    - Mouse wheel zoom
    - Drag to pan
    - Image info overlay (dimensions, size, format)
    - Dark/light theme support
    - Keyboard navigation (Escape to close)

    Usage:
        widgets = [
            ImagePreviewWidgetConfig(
                field="photo",
                thumbnail_size="100px",
                show_info=True,
                zoom_enabled=True,
            )
        ]
    """

    template_name = "django_admin/widgets/image_preview.html"

    class Media:
        css = {
            'all': ('django_admin/css/image_preview.css',)
        }

    def __init__(
        self,
        attrs: Optional[dict[str, Any]] = None,
        thumbnail_size: str = "100px",
        thumbnail_max_width: str = "200px",
        thumbnail_max_height: str = "150px",
        border_radius: str = "8px",
        show_info: bool = True,
        zoom_enabled: bool = True,
        zoom_min: float = 0.5,
        zoom_max: float = 5.0,
        zoom_step: float = 0.1,
        pan_enabled: bool = True,
        show_filename: bool = True,
        show_dimensions: bool = True,
        show_size: bool = True,
        show_format: bool = True,
    ) -> None:
        """
        Initialize the image preview widget.

        Args:
            attrs: Widget attributes
            thumbnail_size: Thumbnail size for preview (default: '100px')
            thumbnail_max_width: Max width for thumbnail (default: '200px')
            thumbnail_max_height: Max height for thumbnail (default: '150px')
            border_radius: Border radius for thumbnail (default: '8px')
            show_info: Show image info in modal (default: True)
            zoom_enabled: Enable mouse wheel zoom (default: True)
            zoom_min: Minimum zoom level (default: 0.5)
            zoom_max: Maximum zoom level (default: 5.0)
            zoom_step: Zoom step per scroll (default: 0.1)
            pan_enabled: Enable drag to pan (default: True)
            show_filename: Show filename in info (default: True)
            show_dimensions: Show dimensions in info (default: True)
            show_size: Show file size in info (default: True)
            show_format: Show format in info (default: True)
        """
        self.thumbnail_size = thumbnail_size
        self.thumbnail_max_width = thumbnail_max_width
        self.thumbnail_max_height = thumbnail_max_height
        self.border_radius = border_radius
        self.show_info = show_info
        self.zoom_enabled = zoom_enabled
        self.zoom_min = zoom_min
        self.zoom_max = zoom_max
        self.zoom_step = zoom_step
        self.pan_enabled = pan_enabled
        self.show_filename = show_filename
        self.show_dimensions = show_dimensions
        self.show_size = show_size
        self.show_format = show_format

        super().__init__(attrs=attrs)

    def get_context(self, name, value, attrs):
        """Add image preview context."""
        context = super().get_context(name, value, attrs)

        # Get image URL if value exists
        image_url = None
        if value and hasattr(value, 'url'):
            image_url = value.url

        # Widget configuration
        context['widget'].update({
            'image_url': image_url,
            'thumbnail_size': self.thumbnail_size,
            'thumbnail_max_width': self.thumbnail_max_width,
            'thumbnail_max_height': self.thumbnail_max_height,
            'border_radius': self.border_radius,
            'show_info': self.show_info,
            'zoom_enabled': self.zoom_enabled,
            'zoom_min': self.zoom_min,
            'zoom_max': self.zoom_max,
            'zoom_step': self.zoom_step,
            'pan_enabled': self.pan_enabled,
            'show_filename': self.show_filename,
            'show_dimensions': self.show_dimensions,
            'show_size': self.show_size,
            'show_format': self.show_format,
        })

        return context
