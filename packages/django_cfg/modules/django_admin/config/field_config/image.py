"""Image field configuration."""

from typing import Any, Dict, Literal, Optional

from pydantic import Field

from .base import FieldConfig


class ImageField(FieldConfig):
    """
    Image widget configuration for displaying images from URLs.

    Universal field for any images including QR codes, avatars, thumbnails, etc.

    Examples:
        # Simple image
        ImageField(name="photo_url", max_width="200px")

        # Image with caption from field
        ImageField(name="thumbnail", max_width="100px", caption_field="title")

        # Circular avatar
        ImageField(name="avatar", width="50px", height="50px", border_radius="50%")

        # QR code with template caption
        ImageField(
            name="get_qr_code_url",
            max_width="200px",
            caption_template="Scan to pay: <code>{pay_address}</code>"
        )
    """

    ui_widget: Literal["image"] = "image"

    width: Optional[str] = Field(None, description="Image width (e.g., '200px', '100%')")
    height: Optional[str] = Field(None, description="Image height (e.g., '200px', 'auto')")
    max_width: Optional[str] = Field("200px", description="Maximum image width")
    max_height: Optional[str] = Field(None, description="Maximum image height")
    border_radius: Optional[str] = Field(None, description="Border radius (e.g., '50%' for circle, '8px')")
    caption: Optional[str] = Field(None, description="Static caption text")
    caption_field: Optional[str] = Field(None, description="Model field name to use as caption")
    caption_template: Optional[str] = Field(None, description="Template string for caption with {field_name} placeholders")
    alt_text: Optional[str] = Field("Image", description="Alt text for image")

    def get_widget_config(self) -> Dict[str, Any]:
        """Extract image widget configuration."""
        config = super().get_widget_config()
        if self.width is not None:
            config['width'] = self.width
        if self.height is not None:
            config['height'] = self.height
        if self.max_width is not None:
            config['max_width'] = self.max_width
        if self.max_height is not None:
            config['max_height'] = self.max_height
        if self.border_radius is not None:
            config['border_radius'] = self.border_radius
        if self.caption is not None:
            config['caption'] = self.caption
        if self.caption_field is not None:
            config['caption_field'] = self.caption_field
        if self.caption_template is not None:
            config['caption_template'] = self.caption_template
        config['alt_text'] = self.alt_text
        return config
