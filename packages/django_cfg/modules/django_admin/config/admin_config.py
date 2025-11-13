"""
Declarative Django Admin configuration.

Type-safe, Pydantic-based admin configuration for Django models.

Quick example:
    admin_config = AdminConfig(
        model=Product,
        list_display=['name', 'price', 'stock'],
        search_fields=['name'],
        list_filter=['category'],
    )

Configuration models:
    - AdminConfig: Main admin configuration (this class)
    - FieldConfig: Field widgets and display options
    - FieldsetConfig: Form organization
    - ActionConfig: Custom admin actions
    - BackgroundTaskConfig: Background task integration
    - ResourceConfig: Related resources (docs, links)

Documentation:
    See ./docs_public/ for full documentation:
    - overview.md - Module overview and features
    - quick-start.md - Getting started guide
    - configuration.md - Complete configuration reference
    - field-types.md - Available field widgets
    - examples.md - Real-world examples
"""

from typing import Any, Dict, List, Optional, Tuple, Type, Union

from django.db import models
from pydantic import BaseModel, ConfigDict, Field

from .action_config import ActionConfig
from .background_task_config import BackgroundTaskConfig
from .documentation_config import DocumentationConfig
from .field_config import FieldConfig
from .fieldset_config import FieldsetConfig
from .resource_config import ResourceConfig


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
    filter_horizontal: List[str] = Field(
        default_factory=list,
        description="M2M fields with horizontal filter widget"
    )
    filter_vertical: List[str] = Field(
        default_factory=list,
        description="M2M fields with vertical filter widget"
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
    resource_class: Optional[Type] = Field(None, description="Custom Resource class for import/export")
    resource_config: Optional[ResourceConfig] = Field(
        None,
        description="Declarative resource configuration (alternative to resource_class)"
    )

    # Background task processing
    background_task_config: Optional[BackgroundTaskConfig] = Field(
        None,
        description="Configuration for background task processing"
    )

    # Documentation
    documentation: Optional[DocumentationConfig] = Field(
        None,
        description="Markdown documentation configuration"
    )

    # Encrypted fields options
    show_encrypted_fields_as_plain_text: bool = Field(
        False,
        description="Show encrypted fields (django-crypto-fields) as plain text instead of password masked. "
                    "WARNING: This exposes sensitive data in the admin interface. Use only in trusted environments."
    )

    # Widget configurations
    widgets: List = Field(
        default_factory=list,
        description="Declarative widget configurations for fields. "
                    "Example: [JSONWidgetConfig(field='config_schema', mode='view', height='500px')]"
    )

    def get_display_field_config(self, field_name: str) -> Optional[FieldConfig]:
        """Get FieldConfig for a specific field."""
        for field_config in self.display_fields:
            if field_config.name == field_name:
                return field_config
        return None

    def to_django_fieldsets(self) -> tuple:
        """Convert fieldsets to Django admin format."""
        return tuple(fs.to_django_fieldset() for fs in self.fieldsets)
