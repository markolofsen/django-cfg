"""Boolean field configuration."""

from typing import Any, Dict, Literal, Optional

from pydantic import Field

from ...icons import Icons
from .base import FieldConfig


class BooleanField(FieldConfig):
    """
    Boolean widget configuration.

    Examples:
        BooleanField(name="is_active")
        BooleanField(name="is_verified", true_icon=Icons.CHECK_CIRCLE)
    """

    ui_widget: Literal["boolean"] = "boolean"

    true_icon: Optional[str] = Field(Icons.CHECK_CIRCLE, description="Icon for True value")
    false_icon: Optional[str] = Field(Icons.CANCEL, description="Icon for False value")

    def get_widget_config(self) -> Dict[str, Any]:
        """Extract boolean widget configuration."""
        config = super().get_widget_config()
        if self.true_icon is not None:
            config['true_icon'] = self.true_icon
        if self.false_icon is not None:
            config['false_icon'] = self.false_icon
        return config
