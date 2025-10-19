"""
Fieldset configuration for declarative admin.
"""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class FieldsetConfig(BaseModel):
    """
    Fieldset configuration.

    Groups related fields together in admin detail view.
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
