"""Text field configuration."""

from typing import Any, Dict, Literal, Optional

from pydantic import Field

from .base import FieldConfig


class TextField(FieldConfig):
    """
    Simple text widget configuration.

    Examples:
        TextField(name="description")
        TextField(name="email", icon=Icons.EMAIL)
        TextField(name="hash", truncate=16, monospace=True)
        TextField(name="message", truncate=100, wrap=True)
    """

    ui_widget: Literal["text"] = "text"

    truncate: Optional[int] = Field(None, description="Truncate text to N characters (e.g., 16, 100)")
    monospace: bool = Field(False, description="Use monospace font (for code, hashes, etc.)")
    wrap: bool = Field(False, description="Wrap text (default: nowrap with ellipsis)")

    def get_widget_config(self) -> Dict[str, Any]:
        """Extract text widget configuration."""
        config = super().get_widget_config()
        if self.truncate is not None:
            config['truncate'] = self.truncate
        config['monospace'] = self.monospace
        config['wrap'] = self.wrap
        return config
