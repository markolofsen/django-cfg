"""Badge field configuration."""

from typing import Any, Dict, Literal, Optional

from pydantic import Field

from .base import FieldConfig


class BadgeField(FieldConfig):
    """
    Badge widget configuration.

    Examples:
        BadgeField(name="status", variant="success")
        BadgeField(name="type", label_map={'active': 'success', 'failed': 'danger'})
    """

    ui_widget: Literal["badge"] = "badge"

    variant: Optional[Literal["primary", "secondary", "success", "danger", "warning", "info"]] = Field(
        None,
        description="Badge color variant"
    )
    label_map: Optional[Dict[Any, str]] = Field(
        None,
        description="Map field values to badge variants: {'active': 'success', 'failed': 'danger'}"
    )

    def get_widget_config(self) -> Dict[str, Any]:
        """Extract badge widget configuration."""
        config = super().get_widget_config()
        if self.variant is not None:
            config['variant'] = self.variant
        if self.label_map is not None:
            config['custom_mappings'] = self.label_map
        return config
