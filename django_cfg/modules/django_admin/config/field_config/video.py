"""Video field configuration with smart URL parsing."""

from typing import Any, Dict, Literal, Optional

from pydantic import Field

from .base import FieldConfig


class VideoField(FieldConfig):
    """
    Video field with smart URL parsing for YouTube, Vimeo, etc.

    Automatically detects video platform and renders appropriate player/thumbnail.

    Examples:
        # Simple video field
        VideoField(name="video_url")

        # With custom thumbnail size
        VideoField(
            name="video_url",
            thumbnail_width=320,
            thumbnail_height=180,
        )

        # Inline player (no modal)
        VideoField(
            name="promo_video",
            show_inline=True,
        )
    """

    ui_widget: Literal["video"] = "video"

    # Thumbnail settings
    thumbnail_width: int = Field(
        200,
        description="Thumbnail width in pixels"
    )
    thumbnail_height: int = Field(
        112,
        description="Thumbnail height in pixels (16:9 ratio)"
    )
    border_radius: int = Field(
        8,
        description="Border radius in pixels"
    )

    # Display options
    show_inline: bool = Field(
        False,
        description="Show inline player instead of thumbnail"
    )
    show_duration: bool = Field(
        True,
        description="Show video duration badge if available"
    )
    show_platform: bool = Field(
        True,
        description="Show platform icon (YouTube, Vimeo, etc.)"
    )

    # Fallback
    fallback_text: Optional[str] = Field(
        None,
        description="Text when URL is invalid or unsupported"
    )

    def get_widget_config(self) -> Dict[str, Any]:
        """Extract video widget configuration."""
        config = super().get_widget_config()

        config['thumbnail_width'] = f"{self.thumbnail_width}px"
        config['thumbnail_height'] = f"{self.thumbnail_height}px"
        config['border_radius'] = f"{self.border_radius}px"
        config['show_inline'] = self.show_inline
        config['show_duration'] = self.show_duration
        config['show_platform'] = self.show_platform

        if self.fallback_text:
            config['fallback_text'] = self.fallback_text

        return config
