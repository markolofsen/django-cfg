"""Image preview field configuration with modal zoom and pan."""

from typing import Any, Dict, Literal, Optional

from pydantic import Field

from .base import FieldConfig


class ImagePreviewField(FieldConfig):
    """
    Image preview widget configuration with modal zoom and pan.

    Click thumbnail to open fullscreen modal with:
    - Mouse wheel zoom
    - Drag to pan
    - Image info display (dimensions, size, format)
    - Keyboard navigation (Escape to close)

    Works with:
    - ImageField (Django file field)
    - URL fields (CharField with image URL)
    - Methods returning image URL

    Examples:
        # Simple preview for ImageField
        ImagePreviewField(name="photo")

        # Preview with custom thumbnail size
        ImagePreviewField(
            name="thumbnail",
            thumbnail_max_width="150px",
            thumbnail_max_height="100px",
        )

        # Circular avatar preview
        ImagePreviewField(
            name="avatar",
            thumbnail_max_width="80px",
            thumbnail_max_height="80px",
            border_radius="50%",
        )

        # Preview from URL field
        ImagePreviewField(
            name="image_url",
            title="Product Image",
            show_info=True,
        )

        # Preview with caption
        ImagePreviewField(
            name="photo",
            caption_field="description",
        )

        # Smart preview - only show for images, fallback for others
        ImagePreviewField(
            name="file",
            url_method="get_download_url",  # Use method to get URL
            condition_field="is_image",      # Only show preview if is_image=True
            fallback_text="Not an image",    # Fallback text
        )
    """

    ui_widget: Literal["image_preview"] = "image_preview"

    # Thumbnail settings
    thumbnail_max_width: int = Field(
        200,
        description="Max width for thumbnail in pixels"
    )
    thumbnail_max_height: int = Field(
        150,
        description="Max height for thumbnail in pixels"
    )
    border_radius: int = Field(
        8,
        description="Border radius for thumbnail in pixels"
    )

    # Info panel settings
    show_info: bool = Field(
        True,
        description="Show image info in modal"
    )
    show_filename: bool = Field(
        True,
        description="Show filename in info panel"
    )
    show_dimensions: bool = Field(
        True,
        description="Show dimensions in info panel"
    )
    show_size: bool = Field(
        True,
        description="Show file size in info panel"
    )
    show_format: bool = Field(
        True,
        description="Show format in info panel"
    )

    # Zoom settings
    zoom_enabled: bool = Field(
        True,
        description="Enable mouse wheel zoom"
    )
    zoom_min: float = Field(
        0.5,
        description="Minimum zoom level"
    )
    zoom_max: float = Field(
        5.0,
        description="Maximum zoom level"
    )
    zoom_step: float = Field(
        0.1,
        description="Zoom step per scroll"
    )

    # Pan settings
    pan_enabled: bool = Field(
        True,
        description="Enable drag to pan"
    )

    # Caption settings (inherited behavior from ImageField)
    caption: Optional[str] = Field(
        None,
        description="Static caption text below thumbnail"
    )
    caption_field: Optional[str] = Field(
        None,
        description="Model field name to use as caption"
    )
    caption_template: Optional[str] = Field(
        None,
        description="Template string for caption with {field_name} placeholders"
    )

    # Alt text
    alt_text: str = Field(
        "Image",
        description="Alt text for image"
    )

    # Smart URL resolution
    url_method: Optional[str] = Field(
        None,
        description="Model method name that returns image URL (e.g., 'get_download_url')"
    )

    # Fallback field - if main field is empty, try this field
    fallback_field: Optional[str] = Field(
        None,
        description="Fallback field name if main field is empty (supports __ notation for FK)"
    )

    # Conditional display
    condition_field: Optional[str] = Field(
        None,
        description="Model field/property to check for showing preview (e.g., 'is_image')"
    )
    condition_value: Any = Field(
        True,
        description="Expected value for condition_field (default: True)"
    )

    # Fallback when condition not met
    fallback_text: Optional[str] = Field(
        None,
        description="Text to show when condition is not met"
    )
    fallback_badge_variant: str = Field(
        "secondary",
        description="Badge variant for fallback (primary, secondary, success, danger, warning, info)"
    )

    def get_widget_config(self) -> Dict[str, Any]:
        """Extract image preview widget configuration."""
        config = super().get_widget_config()

        # Thumbnail settings (convert int to px)
        config['thumbnail_max_width'] = f"{self.thumbnail_max_width}px"
        config['thumbnail_max_height'] = f"{self.thumbnail_max_height}px"
        config['border_radius'] = f"{self.border_radius}px"

        # Info panel
        config['show_info'] = self.show_info
        config['show_filename'] = self.show_filename
        config['show_dimensions'] = self.show_dimensions
        config['show_size'] = self.show_size
        config['show_format'] = self.show_format

        # Zoom
        config['zoom_enabled'] = self.zoom_enabled
        config['zoom_min'] = self.zoom_min
        config['zoom_max'] = self.zoom_max
        config['zoom_step'] = self.zoom_step

        # Pan
        config['pan_enabled'] = self.pan_enabled

        # Caption
        if self.caption is not None:
            config['caption'] = self.caption
        if self.caption_field is not None:
            config['caption_field'] = self.caption_field
        if self.caption_template is not None:
            config['caption_template'] = self.caption_template

        config['alt_text'] = self.alt_text

        # Smart URL resolution
        if self.url_method is not None:
            config['url_method'] = self.url_method

        # Fallback field
        if self.fallback_field is not None:
            config['fallback_field'] = self.fallback_field

        # Conditional display
        if self.condition_field is not None:
            config['condition_field'] = self.condition_field
            config['condition_value'] = self.condition_value

        # Fallback
        if self.fallback_text is not None:
            config['fallback_text'] = self.fallback_text
        config['fallback_badge_variant'] = self.fallback_badge_variant

        return config
