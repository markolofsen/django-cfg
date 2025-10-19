"""
Main admin configuration for declarative admin.
"""

from typing import Any, Dict, List, Optional, Tuple, Type, Union

from django.db import models
from pydantic import BaseModel, ConfigDict, Field

from .action_config import ActionConfig
from .field_config import FieldConfig
from .fieldset_config import FieldsetConfig


class AdminConfig(BaseModel):
    """
    Main admin configuration.

    Complete declarative configuration for ModelAdmin.
    """

    model_config = ConfigDict(validate_assignment=True, extra="forbid", arbitrary_types_allowed=True)

    # Model
    model: Type[models.Model] = Field(..., description="Django model class")

    # List display
    list_display: List[str] = Field(..., description="Fields to display in list view")
    list_display_links: List[str] = Field(
        default_factory=list,
        description="Fields that should be linked to change form"
    )
    display_fields: List[FieldConfig] = Field(
        default_factory=list,
        description="Field configurations with widgets"
    )

    # Filters and search
    list_filter: List[Union[str, Type, Tuple[str, Type]]] = Field(
        default_factory=list,
        description="List filters (supports strings, filter classes, and tuples like ('field', FilterClass))"
    )
    search_fields: List[str] = Field(
        default_factory=list,
        description="Searchable fields"
    )

    # Ordering
    ordering: List[str] = Field(
        default_factory=list,
        description="Default ordering"
    )

    # Readonly fields
    readonly_fields: List[str] = Field(
        default_factory=list,
        description="Read-only fields"
    )

    # Fieldsets
    fieldsets: List[FieldsetConfig] = Field(
        default_factory=list,
        description="Fieldset configurations"
    )

    # Actions
    actions: List[ActionConfig] = Field(
        default_factory=list,
        description="Custom actions"
    )

    # Performance optimization
    select_related: List[str] = Field(
        default_factory=list,
        description="Fields for select_related()"
    )
    prefetch_related: List[str] = Field(
        default_factory=list,
        description="Fields for prefetch_related()"
    )
    annotations: Dict[str, Any] = Field(
        default_factory=dict,
        description="Query annotations (e.g., Count, Sum, etc.)"
    )

    # Pagination
    list_per_page: int = Field(50, description="Items per page")
    list_max_show_all: int = Field(200, description="Max items for 'show all'")

    # Form options
    autocomplete_fields: List[str] = Field(
        default_factory=list,
        description="Fields with autocomplete widget"
    )
    raw_id_fields: List[str] = Field(
        default_factory=list,
        description="Fields with raw ID widget"
    )
    prepopulated_fields: Dict[str, tuple] = Field(
        default_factory=dict,
        description="Auto-populate fields (e.g., {'slug': ('name',)})"
    )
    formfield_overrides: Dict[Type, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Form field overrides (e.g., {TextField: {'widget': WysiwygWidget}})"
    )

    # Inlines
    inlines: List[Type] = Field(
        default_factory=list,
        description="Inline model admin classes"
    )

    # Extra options
    date_hierarchy: Optional[str] = Field(None, description="Date hierarchy field")
    save_on_top: bool = Field(False, description="Show save buttons on top")
    save_as: bool = Field(False, description="Enable 'save as new'")
    preserve_filters: bool = Field(True, description="Preserve filters on save")

    # Import/Export options
    import_export_enabled: bool = Field(False, description="Enable import/export functionality")
    resource_class: Optional[Type] = Field(None, description="Resource class for import/export")

    def get_display_field_config(self, field_name: str) -> Optional[FieldConfig]:
        """Get FieldConfig for a specific field."""
        for field_config in self.display_fields:
            if field_config.name == field_name:
                return field_config
        return None

    def to_django_fieldsets(self) -> tuple:
        """Convert fieldsets to Django admin format."""
        return tuple(fs.to_django_fieldset() for fs in self.fieldsets)
