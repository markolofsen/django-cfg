"""Short UUID field configuration."""

from typing import Any, Dict, Literal

from pydantic import Field

from .base import FieldConfig


class ShortUUIDField(FieldConfig):
    """
    Short UUID widget configuration for displaying shortened UUIDs.

    Examples:
        ShortUUIDField(name="id", length=8)
        ShortUUIDField(name="uuid", length=12, copy_on_click=True)
    """

    ui_widget: Literal["short_uuid"] = "short_uuid"

    length: int = Field(8, description="Number of characters to display from UUID")
    copy_on_click: bool = Field(True, description="Enable click-to-copy functionality")
    show_full_on_hover: bool = Field(True, description="Show full UUID in tooltip on hover")

    def get_widget_config(self) -> Dict[str, Any]:
        """Extract short UUID widget configuration."""
        config = super().get_widget_config()
        config['length'] = self.length
        config['copy_on_click'] = self.copy_on_click
        config['show_full_on_hover'] = self.show_full_on_hover
        return config
