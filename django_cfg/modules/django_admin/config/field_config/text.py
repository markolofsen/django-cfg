"""Text field configuration."""

from typing import Any, Dict, Literal, Optional

from pydantic import Field

from .base import FieldConfig


class TextField(FieldConfig):
    """
    Text widget with truncation and styling.

    Examples:
        TextField(name="description")
        TextField(name="email", icon=Icons.EMAIL)
        TextField(name="hash", truncate=16, monospace=True)
        TextField(name="message", truncate=60, max_width="400px")
    """

    ui_widget: Literal["text"] = "text"

    truncate: Optional[int] = Field(None, description="Truncate text to N characters")
    monospace: bool = Field(False, description="Use monospace font")
    nowrap: bool = Field(True, description="Prevent line wrapping (default: True)")
    max_width: str = Field("300px", description="CSS max-width for text cell")
    show_tooltip: bool = Field(True, description="Show full text on hover when truncated")

    def get_widget_config(self) -> Dict[str, Any]:
        """Extract text widget configuration."""
        config = super().get_widget_config()
        if self.truncate is not None:
            config['truncate'] = self.truncate
        config['monospace'] = self.monospace
        config['nowrap'] = self.nowrap
        config['max_width'] = self.max_width
        config['show_tooltip'] = self.show_tooltip
        return config
