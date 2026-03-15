"""
Widget configuration models for declarative admin.

Pydantic models for type-safe widget configuration.
"""

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class WidgetConfig(BaseModel):
    """
    Base widget configuration.

    All widget configs must specify which field they apply to.
    """

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    field: str = Field(..., description="Model field name this widget applies to")

    def to_widget_kwargs(self) -> dict:
        """Convert to widget initialization kwargs. Override in subclasses."""
        return {}


class JSONWidgetConfig(WidgetConfig):
    """
    Configuration for JSON editor widget.

    Example:
        JSONWidgetConfig(
            field="config_schema",
            mode="view",
            height="500px",
            show_copy_button=True
        )
    """

    mode: Literal["tree", "code", "view"] = Field(
        "code",
        description="Editor mode: 'code' (text editor - default), 'tree' (interactive), 'view' (read-only)"
    )
    height: Optional[str] = Field(
        "400px",
        description="Editor height (e.g., '400px', '50vh')"
    )
    width: Optional[str] = Field(
        None,
        description="Editor width (e.g., '100%', '600px')"
    )
    show_copy_button: bool = Field(
        True,
        description="Show copy-to-clipboard button"
    )

    def to_widget_kwargs(self) -> dict:
        """Convert to widget initialization kwargs."""
        kwargs = {
            'mode': self.mode,
            'height': self.height,
            'show_copy_button': self.show_copy_button,
        }
        if self.width:
            kwargs['width'] = self.width
        return kwargs


class TextWidgetConfig(WidgetConfig):
    """
    Configuration for text input widgets.

    Example:
        TextWidgetConfig(
            field="description",
            placeholder="Enter value",
            max_length=100
        )
    """

    placeholder: Optional[str] = Field(None, description="Placeholder text")
    max_length: Optional[int] = Field(None, description="Maximum length")
    rows: Optional[int] = Field(None, description="Number of rows for textarea")

    def to_widget_kwargs(self) -> dict:
        """Convert to widget initialization kwargs."""
        kwargs = {}
        if self.placeholder:
            kwargs['placeholder'] = self.placeholder
        if self.max_length:
            kwargs['max_length'] = self.max_length
        if self.rows:
            kwargs['rows'] = self.rows
        return kwargs


class ImagePreviewWidgetConfig(WidgetConfig):
    """
    Configuration for image preview widget with modal zoom and pan.

    Features:
    - Click thumbnail to open fullscreen modal
    - Mouse wheel zoom
    - Drag to pan
    - Image info display (dimensions, size, format)

    Example:
        ImagePreviewWidgetConfig(
            field="photo",
            thumbnail_max_width=200,
            thumbnail_max_height=150,
            show_info=True,
            zoom_enabled=True,
        )
    """

    thumbnail_size: int = Field(
        100,
        description="Thumbnail size for preview in pixels"
    )
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
    show_info: bool = Field(
        True,
        description="Show image info in modal (dimensions, size, format)"
    )
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
    pan_enabled: bool = Field(
        True,
        description="Enable drag to pan"
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

    def to_widget_kwargs(self) -> dict:
        """Convert to widget initialization kwargs."""
        return {
            'thumbnail_size': f"{self.thumbnail_size}px",
            'thumbnail_max_width': f"{self.thumbnail_max_width}px",
            'thumbnail_max_height': f"{self.thumbnail_max_height}px",
            'border_radius': f"{self.border_radius}px",
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
        }
