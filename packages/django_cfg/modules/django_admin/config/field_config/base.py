"""
Base field configuration class.

Type-safe field configurations with widget-specific classes.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class FieldConfig(BaseModel):
    """
    Base field display configuration.

    Use specialized subclasses for type safety:
    - BadgeField: Badge widget with variants
    - CurrencyField: Currency/money display
    - DateTimeField: DateTime with relative time
    - UserField: User display with avatar
    - TextField: Simple text display
    - BooleanField: Boolean icons
    """

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    # Basic field info
    name: str = Field(..., description="Field name from model")
    title: Optional[str] = Field(None, description="Display title (defaults to field name)")

    # UI widget configuration
    ui_widget: Optional[str] = Field(
        None,
        description="Widget name: 'badge', 'currency', 'user_avatar', 'datetime_relative', etc."
    )

    # Display options
    header: bool = Field(False, description="Use header display")
    ordering: Optional[str] = Field(None, description="Field name for sorting")
    empty_value: str = Field("—", description="Value to display when field is empty")

    # Icon
    icon: Optional[str] = Field(None, description="Material icon name")

    # Advanced
    css_class: Optional[str] = Field(None, description="Custom CSS classes")
    tooltip: Optional[str] = Field(None, description="Tooltip text")

    def get_widget_config(self) -> Dict[str, Any]:
        """Extract widget-specific configuration."""
        config = {}
        if self.icon is not None:
            config['icon'] = self.icon
        return config
