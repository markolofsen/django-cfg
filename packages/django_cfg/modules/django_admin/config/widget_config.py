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
