"""
Fieldset configuration for declarative admin.
"""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class FieldsetConfig(BaseModel):
    """
    Fieldset configuration.

    Groups related fields together in admin detail view.

    Example:
        FieldsetConfig(
            title="Basic Info",
            fields=["id", "name", "description"],
        )

        FieldsetConfig(
            title="Advanced Settings",
            fields=["config", "metadata"],
            collapsed=True,
            description="Additional configuration options"
        )

    Note: For widget configuration, use AdminConfig.widgets instead:
        AdminConfig(
            model=MyModel,
            widgets=[
                JSONWidgetConfig(field="config", mode="view", height="500px"),
            ],
            fieldsets=[
                FieldsetConfig(title="Config", fields=["config"]),
            ]
        )
    """

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    title: str = Field(..., description="Fieldset title")
    fields: List[str] = Field(..., description="List of field names")
    collapsed: bool = Field(False, description="Start collapsed")
    css_class: Optional[str] = Field(None, description="Custom CSS class")
    description: Optional[str] = Field(None, description="Fieldset description")

    def to_django_fieldset(self) -> tuple:
        """Convert to Django admin fieldset format."""
        options = {
            'fields': tuple(self.fields)
        }

        # Build classes list
        classes = []
        if self.collapsed:
            classes.append('collapse')
        if self.css_class:
            classes.append(self.css_class)

        if classes:
            options['classes'] = tuple(classes)

        if self.description:
            options['description'] = self.description

        return (self.title, options)
