"""DateTime field configuration."""

from typing import Any, Dict, Literal, Optional

from pydantic import Field

from .base import FieldConfig


class DateTimeField(FieldConfig):
    """
    DateTime widget configuration.

    Examples:
        DateTimeField(name="created_at", show_relative=True)
        DateTimeField(name="updated_at", datetime_format="%Y-%m-%d %H:%M")
        DateTimeField(name="posted_at", use_local_tz=True)  # Convert to local timezone
        DateTimeField(name="server_time", use_local_tz=False)  # Keep original timezone
    """

    ui_widget: Literal["datetime_relative"] = "datetime_relative"

    datetime_format: Optional[str] = Field(None, description="DateTime format string")
    show_relative: bool = Field(True, description="Show relative time (e.g., '2 hours ago')")
    use_local_tz: bool = Field(True, description="Convert to local timezone (default: True)")

    def get_widget_config(self) -> Dict[str, Any]:
        """Extract datetime widget configuration."""
        config = super().get_widget_config()
        if self.datetime_format is not None:
            config['datetime_format'] = self.datetime_format
        config['show_relative'] = self.show_relative
        config['use_local_tz'] = self.use_local_tz
        return config
