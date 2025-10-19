"""
Registry Admin v2.0 - NEW Declarative Pydantic Approach

Enhanced agent and template management with Material Icons and clean declarative config.
"""

from django.contrib import admin, messages
from django.db import models
from django.db.models.fields.json import JSONField
from django_json_widget.widgets import JSONEditorWidget
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import AutocompleteSelectFilter
from unfold.contrib.forms.widgets import WysiwygWidget

from django_cfg import ExportForm
from django_cfg.modules.django_admin import (
    ActionConfig,
    AdminConfig,
    BadgeField,
    TextField,
    UserField,
    DateTimeField,
    FieldsetConfig,
    Icons,
    computed_field,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from ..models.registry import AgentDefinition, AgentTemplate
from .registry_actions import (
    activate_agents,
    deactivate_agents,
    reset_stats,
    make_public,
    make_private,
    duplicate_templates,
)


# ===== Agent Definition Admin Config =====

agent_definition_config = AdminConfig(
    model=AgentDefinition,

    # Performance optimization
    select_related=['created_by'],

    # Import/Export
    import_export_enabled=True,

    # List display
    list_display=[
        "name_display",
        "category_display",
        "status_display",
        "version_display",
        "usage_stats_display",
        "performance_metrics",
        "created_by_display",
        "created_at_display"
    ],

    # Display fields with UI widgets
    display_fields=[
        BadgeField(
            name="name",
            title="Agent Name",
            variant="primary",
            icon=Icons.SMART_TOY,
            header=True
        ),
        BadgeField(
            name="category",
            title="Category",
            variant="secondary",
            icon=Icons.CATEGORY
        ),
        BadgeField(
            name="status",
            title="Status"
        ),
        TextField(
            name="version",
            title="Version"
        ),
        UserField(
            name="created_by",
            title="Created By"
        ),
        DateTimeField(
            name="created_at",
            title="Created",
            ordering="created_at"
        ),
    ],

    # Search and filters
    search_fields=["name", "description", "category"],
    list_filter=[
        "category",
        "is_active",
        "created_at",
        ("created_by", AutocompleteSelectFilter)
    ],

    # Actions
    actions=[
        ActionConfig(
            name="activate_agents",
            description="Activate agents",
            variant="success",
            icon=Icons.CHECK_CIRCLE,
            handler=activate_agents
        ),
        ActionConfig(
            name="deactivate_agents",
            description="Deactivate agents",
            variant="warning",
            icon=Icons.CANCEL,
            handler=deactivate_agents
        ),
        ActionConfig(
            name="reset_stats",
            description="Reset statistics",
            variant="danger",
            icon=Icons.REFRESH,
            confirmation=True,
            handler=reset_stats
        ),
    ],

    # Ordering
    ordering=["-created_at"],
)


@admin.register(AgentDefinition)
class AgentDefinitionAdmin(PydanticAdmin):
    """
    Agent Definition admin using NEW Pydantic declarative approach.

    Features:
    - Declarative configuration with type safety
    - Automatic display method generation
    - Material Icons integration
    - Export functionality (via config)
    - Custom actions for agent activation/deactivation
    - Performance metrics display
    """
    config = agent_definition_config

    # Readonly fields
    readonly_fields = ["id", "created_at", "updated_at", "usage_count", "last_used_at"]

    # Fieldsets
    fieldsets = [
        FieldsetConfig(
            title="Agent Info",
            fields=['name', 'description', 'category', 'version']
        ),
        FieldsetConfig(
            title="Configuration",
            fields=['config', 'capabilities', 'requirements']
        ),
        FieldsetConfig(
            title="Performance",
            fields=['usage_count', 'success_rate', 'avg_execution_time', 'total_cost']
        ),
        FieldsetConfig(
            title="Status",
            fields=['status', 'is_active']
        ),
        FieldsetConfig(
            title="Metadata",
            fields=['created_by', 'updated_by', 'created_at', 'updated_at'],
            collapsed=True
        ),
    ]

    # Custom display methods using @computed_field decorator
    @computed_field("Agent Name")
    def name_display(self, obj: AgentDefinition) -> str:
        """Enhanced agent name display."""
        return self.html.badge(obj.name, variant="primary", icon=Icons.SMART_TOY)

    @computed_field("Category")
    def category_display(self, obj: AgentDefinition) -> str:
        """Category display with badge."""
        if not obj.category:
            return "—"

        category_variants = {
            'automation': 'info',
            'analysis': 'success',
            'communication': 'warning',
            'data': 'primary'
        }
        variant = category_variants.get(obj.category.lower(), 'secondary')

        return self.html.badge(obj.category.title(), variant=variant, icon=Icons.CATEGORY)

    @computed_field("Status")
    def status_display(self, obj: AgentDefinition) -> str:
        """Status display with appropriate icons."""
        icon_map = {
            'active': Icons.CHECK_CIRCLE,
            'testing': Icons.WARNING,
            'archived': Icons.ARCHIVE,
            'draft': Icons.EDIT,
            'deprecated': Icons.CANCEL
        }

        variant_map = {
            'draft': 'secondary',
            'testing': 'warning',
            'active': 'success',
            'deprecated': 'danger',
            'archived': 'info'
        }

        icon = icon_map.get(obj.status, Icons.EDIT)
        variant = variant_map.get(obj.status, 'secondary')
        text = obj.get_status_display() if hasattr(obj, 'get_status_display') else obj.status.title()
        return self.html.badge(text, variant=variant, icon=icon)

    @computed_field("Version")
    def version_display(self, obj: AgentDefinition) -> str:
        """Version display."""
        if not obj.version:
            return "—"
        return f"v{obj.version}"

    @computed_field("Usage Stats")
    def usage_stats_display(self, obj: AgentDefinition) -> str:
        """Display usage statistics."""
        if not obj.usage_count:
            return "No usage"

        success_rate = obj.success_rate or 0
        return f"{obj.usage_count} uses, {success_rate:.1f}% success"

    @computed_field("Performance")
    def performance_metrics(self, obj: AgentDefinition) -> str:
        """Display performance metrics."""
        if not obj.avg_execution_time:
            return "No data"

        avg_time = obj.avg_execution_time
        if obj.total_cost:
            cost = MoneyDisplay.amount(obj.total_cost, config)
            return f"{avg_time:.2f}s avg, {cost} total"

        return f"{avg_time:.2f}s avg"

    @computed_field("Created By")
    def created_by_display(self, obj: AgentDefinition) -> str:
        """Created by user display."""
        if not obj.created_by:
            return "—"
        # Simple username display, UserField handles avatar and styling
        return obj.created_by.username

    @computed_field("Created")
    def created_at_display(self, obj: AgentDefinition) -> str:
        """Created time with relative display."""
        # DateTimeField in display_fields handles formatting automatically
        return obj.created_at


# ===== Agent Template Admin Config =====

agent_template_config = AdminConfig(
    model=AgentTemplate,

    # Performance optimization
    select_related=['created_by'],

    # Import/Export
    import_export_enabled=True,

    # List display
    list_display=[
        "name_display",
        "category_display",
        "status_display",
        "usage_count_display",
        "created_by_display",
        "created_at_display"
    ],

    # Display fields with UI widgets
    display_fields=[
        BadgeField(
            name="name",
            title="Template Name",
            variant="primary",
            icon=Icons.DESCRIPTION,
            header=True
        ),
        BadgeField(
            name="category",
            title="Category",
            variant="secondary",
            icon=Icons.CATEGORY
        ),
        UserField(
            name="created_by",
            title="Created By"
        ),
        DateTimeField(
            name="created_at",
            title="Created",
            ordering="created_at"
        ),
    ],

    # Search and filters
    search_fields=["name", "description", "category"],
    list_filter=[
        "category",
        "created_at",
        ("created_by", AutocompleteSelectFilter)
    ],

    # Actions
    actions=[
        ActionConfig(
            name="make_public",
            description="Make public",
            variant="success",
            icon=Icons.PUBLIC,
            handler=make_public
        ),
        ActionConfig(
            name="make_private",
            description="Make private",
            variant="warning",
            icon=Icons.LOCK,
            handler=make_private
        ),
        ActionConfig(
            name="duplicate_templates",
            description="Duplicate templates",
            variant="primary",
            icon=Icons.CONTENT_COPY,
            handler=duplicate_templates
        ),
    ],

    # Ordering
    ordering=["-created_at"],
)


@admin.register(AgentTemplate)
class AgentTemplateAdmin(PydanticAdmin):
    """
    Agent Template admin using NEW Pydantic declarative approach.

    Features:
    - Declarative configuration with type safety
    - Automatic display method generation
    - Material Icons integration
    - Export functionality (via config)
    - Custom actions for template visibility
    - Usage tracking
    """
    config = agent_template_config

    # Readonly fields
    readonly_fields = ["id", "created_at", "updated_at"]

    # Fieldsets
    fieldsets = [
        FieldsetConfig(
            title="Template Info",
            fields=['name', 'description', 'category']
        ),
        FieldsetConfig(
            title="Template Content",
            fields=['template_config', 'use_cases']
        ),
        FieldsetConfig(
            title="Settings",
            fields=['is_public', 'usage_count']
        ),
        FieldsetConfig(
            title="Metadata",
            fields=['created_by', 'updated_by', 'created_at', 'updated_at'],
            collapsed=True
        ),
    ]

    # Custom display methods using @computed_field decorator
    @computed_field("Template Name")
    def name_display(self, obj: AgentTemplate) -> str:
        """Enhanced template name display."""
        return self.html.badge(obj.name, variant="primary", icon=Icons.DESCRIPTION)

    @computed_field("Category")
    def category_display(self, obj: AgentTemplate) -> str:
        """Category display with badge."""
        if not obj.category:
            return "—"

        category_variants = {
            'automation': 'info',
            'analysis': 'success',
            'communication': 'warning',
            'data': 'primary'
        }
        variant = category_variants.get(obj.category.lower(), 'secondary')

        return self.html.badge(obj.category.title(), variant=variant, icon=Icons.CATEGORY)

    @computed_field("Status")
    def status_display(self, obj: AgentTemplate) -> str:
        """Status display based on public/private."""
        if obj.is_public:
            return self.html.badge("Public", variant="success", icon=Icons.PUBLIC)
        else:
            return self.html.badge("Private", variant="secondary", icon=Icons.LOCK)

    @computed_field("Usage")
    def usage_count_display(self, obj: AgentTemplate) -> str:
        """Usage count display."""
        if not obj.usage_count:
            return "Not used"
        return f"{obj.usage_count} times"

    @computed_field("Created By")
    def created_by_display(self, obj: AgentTemplate) -> str:
        """Created by user display."""
        if not obj.created_by:
            return "—"
        # Simple username display, UserField handles avatar and styling
        return obj.created_by.username

    @computed_field("Created")
    def created_at_display(self, obj: AgentTemplate) -> str:
        """Created time with relative display."""
        # DateTimeField in display_fields handles formatting automatically
        return obj.created_at
