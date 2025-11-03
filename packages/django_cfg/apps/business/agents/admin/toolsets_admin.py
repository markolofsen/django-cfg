"""
Toolsets Admin v2.0 - NEW Declarative Pydantic Approach

Enhanced toolset management with Material Icons and clean declarative config.
"""

from django.contrib import admin
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

from ..models.toolsets import ApprovalLog, ToolExecution, ToolsetConfiguration
from .toolsets_actions import (
    retry_failed_executions,
    clear_errors,
    approve_pending,
    reject_pending,
    extend_expiry,
    activate_configurations,
    deactivate_configurations,
    reset_usage,
)


# ===== Tool Execution Admin Config =====

tool_execution_config = AdminConfig(
    model=ToolExecution,

    # Performance optimization
    select_related=['agent_execution', 'user'],

    # Import/Export
    import_export_enabled=True,

    # List display
    list_display=[
        'id_display',
        'tool_name_display',
        'toolset_display',
        'status_display',
        'duration_display',
        'retry_count_display',
        'created_at_display'
    ],

    # Display fields with UI widgets
    display_fields=[
        BadgeField(
            name="id",
            title="ID",
            variant="secondary",
            icon=Icons.TAG,
            header=True
        ),
        BadgeField(
            name="tool_name",
            title="Tool",
            variant="primary",
            icon=Icons.BUILD
        ),
        BadgeField(
            name="toolset_class",
            title="Toolset",
            variant="info",
            icon=Icons.EXTENSION
        ),
        BadgeField(
            name="status",
            title="Status"
        ),
        TextField(
            name="execution_time",
            title="Duration"
        ),
        BadgeField(
            name="retry_count",
            title="Retries",
            variant="warning",
            icon=Icons.REFRESH
        ),
        DateTimeField(
            name="created_at",
            title="Created",
            ordering="created_at"
        ),
    ],

    # Search and filters
    search_fields=['tool_name', 'toolset_name', 'arguments', 'result'],
    list_filter=[
        'status',
        'tool_name',
        'created_at',
        ('agent_execution', AutocompleteSelectFilter)
    ],

    # List display links
    list_display_links=['id_display', 'tool_name_display'],

    # Autocomplete fields
    autocomplete_fields=['agent_execution'],

    # Form field overrides
    formfield_overrides={
        models.TextField: {"widget": WysiwygWidget},
        JSONField: {"widget": JSONEditorWidget},
    },

    # Actions
    actions=[
        ActionConfig(
            name="retry_failed_executions",
            description="Retry failed executions",
            variant="warning",
            icon=Icons.REFRESH,
            handler=retry_failed_executions
        ),
        ActionConfig(
            name="clear_errors",
            description="Clear error messages",
            variant="primary",
            icon=Icons.DELETE,
            handler=clear_errors
        ),
    ],

    # Ordering
    ordering=['-created_at'],
)


@admin.register(ToolExecution)
class ToolExecutionAdmin(PydanticAdmin):
    """
    Tool Execution admin using NEW Pydantic declarative approach.

    Features:
    - Declarative configuration with type safety
    - Automatic display method generation
    - Material Icons integration
    - Export functionality (via config)
    - Retry and error management actions
    """
    config = tool_execution_config

    # Readonly fields
    readonly_fields = ['id', 'execution_time', 'retry_count', 'created_at', 'started_at', 'completed_at']

    # Fieldsets
    fieldsets = [
        FieldsetConfig(
            title="Tool Info",
            fields=['tool_name', 'toolset_class', 'agent_execution']
        ),
        FieldsetConfig(
            title="Execution Data",
            fields=['arguments', 'result', 'error_message']
        ),
        FieldsetConfig(
            title="Metrics",
            fields=['execution_time', 'retry_count', 'status']
        ),
        FieldsetConfig(
            title="Approval",
            fields=['approval_log'],
            collapsed=True
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=['created_at', 'started_at', 'completed_at'],
            collapsed=True
        ),
    ]

    # Custom display methods using @computed_field decorator
    @computed_field("ID")
    def id_display(self, obj: ToolExecution) -> str:
        """Enhanced ID display."""
        return self.html.badge(f"#{str(obj.id)[:8]}", variant="secondary", icon=Icons.TAG)

    @computed_field("Tool")
    def tool_name_display(self, obj: ToolExecution) -> str:
        """Enhanced tool name display."""
        return self.html.badge(obj.tool_name, variant="primary", icon=Icons.BUILD)

    @computed_field("Toolset")
    def toolset_display(self, obj: ToolExecution) -> str:
        """Toolset class display with badge."""
        if not obj.toolset_class:
            return "—"

        # Extract class name from full path
        class_name = obj.toolset_class.split('.')[-1] if '.' in obj.toolset_class else obj.toolset_class

        return self.html.badge(class_name, variant="info", icon=Icons.EXTENSION)

    @computed_field("Status")
    def status_display(self, obj: ToolExecution) -> str:
        """Status display with appropriate icons."""
        icon_map = {
            'running': Icons.PLAY_ARROW,
            'completed': Icons.CHECK_CIRCLE,
            'failed': Icons.ERROR,
            'pending': Icons.SCHEDULE,
            'cancelled': Icons.CANCEL
        }

        variant_map = {
            'pending': 'warning',
            'running': 'info',
            'completed': 'success',
            'failed': 'danger',
            'cancelled': 'secondary'
        }

        icon = icon_map.get(obj.status, Icons.SCHEDULE)
        variant = variant_map.get(obj.status, 'warning')
        text = obj.get_status_display() if hasattr(obj, 'get_status_display') else obj.status.title()
        return self.html.badge(text, variant=variant, icon=icon)

    @computed_field("Duration")
    def duration_display(self, obj: ToolExecution) -> str:
        """Execution duration display."""
        if obj.execution_time:
            return f"{obj.execution_time:.3f}s"
        return "—"

    @computed_field("Retries")
    def retry_count_display(self, obj: ToolExecution) -> str:
        """Retry count display with badge."""
        if obj.retry_count > 0:
            variant = "warning" if obj.retry_count > 2 else "info"
            return self.html.badge(str(obj.retry_count), variant=variant
            )
        return "0"

    @computed_field("Created")
    def created_at_display(self, obj: ToolExecution) -> str:
        """Created time with relative display."""
        # DateTimeField in display_fields handles formatting automatically
        return obj.created_at


# ===== Approval Log Admin Config =====

approval_log_config = AdminConfig(
    model=ApprovalLog,

    # Performance optimization
    select_related=['approved_by'],

    # Import/Export
    import_export_enabled=True,

    # List display
    list_display=[
        'approval_id_display',
        'tool_name_display',
        'status_display',
        'approved_by_display',
        'decision_time_display',
        'expires_at_display'
    ],

    # Display fields with UI widgets
    display_fields=[
        BadgeField(
            name="id",
            title="Approval ID",
            variant="secondary",
            icon=Icons.VERIFIED,
            header=True
        ),
        BadgeField(
            name="tool_name",
            title="Tool",
            variant="primary",
            icon=Icons.BUILD
        ),
        BadgeField(
            name="status",
            title="Status"
        ),
        UserField(
            name="approved_by",
            title="Approved By"
        ),
        TextField(
            name="decision_time",
            title="Decision Time"
        ),
        DateTimeField(
            name="expires_at",
            title="Expires"
        ),
    ],

    # Search and filters
    search_fields=['tool_name', 'tool_args', 'justification'],
    list_filter=[
        'status',
        'tool_name',
        'requested_at',
        'expires_at',
        ('approved_by', AutocompleteSelectFilter)
    ],

    # List display links
    list_display_links=['approval_id_display', 'tool_name_display'],

    # Autocomplete fields
    autocomplete_fields=['approved_by'],

    # Form field overrides
    formfield_overrides={
        models.TextField: {"widget": WysiwygWidget},
        JSONField: {"widget": JSONEditorWidget},
    },

    # Actions
    actions=[
        ActionConfig(
            name="approve_pending",
            description="Approve pending",
            variant="success",
            icon=Icons.CHECK_CIRCLE,
            handler=approve_pending
        ),
        ActionConfig(
            name="reject_pending",
            description="Reject pending",
            variant="danger",
            icon=Icons.CANCEL,
            confirmation=True,
            handler=reject_pending
        ),
        ActionConfig(
            name="extend_expiry",
            description="Extend expiry",
            variant="warning",
            icon=Icons.TIMER,
            handler=extend_expiry
        ),
    ],

    # Ordering
    ordering=['-requested_at'],
)


@admin.register(ApprovalLog)
class ApprovalLogAdmin(PydanticAdmin):
    """
    Approval Log admin using NEW Pydantic declarative approach.

    Features:
    - Declarative configuration with type safety
    - Automatic display method generation
    - Material Icons integration
    - Export functionality (via config)
    - Approval management actions
    """
    config = approval_log_config

    # Readonly fields
    readonly_fields = ['id', 'requested_at', 'decided_at', 'expires_at']

    # Fieldsets
    fieldsets = [
        FieldsetConfig(
            title="Approval Info",
            fields=['tool_name', 'status', 'approved_by']
        ),
        FieldsetConfig(
            title="Request Details",
            fields=['tool_arguments', 'justification']
        ),
        FieldsetConfig(
            title="Timing",
            fields=['decision_time', 'expires_at']
        ),
    ]

    # Custom display methods using @computed_field decorator
    @computed_field("Approval ID")
    def approval_id_display(self, obj: ApprovalLog) -> str:
        """Enhanced approval ID display."""
        return self.html.badge(f"#{str(obj.id)[:8]}", variant="secondary", icon=Icons.VERIFIED)

    @computed_field("Tool")
    def tool_name_display(self, obj: ApprovalLog) -> str:
        """Enhanced tool name display."""
        return self.html.badge(obj.tool_name, variant="primary", icon=Icons.BUILD)

    @computed_field("Status")
    def status_display(self, obj: ApprovalLog) -> str:
        """Status display with appropriate icons."""
        icon_map = {
            'approved': Icons.CHECK_CIRCLE,
            'rejected': Icons.CANCEL,
            'pending': Icons.SCHEDULE,
            'expired': Icons.TIMER_OFF
        }

        variant_map = {
            'pending': 'warning',
            'approved': 'success',
            'rejected': 'danger',
            'expired': 'secondary'
        }

        icon = icon_map.get(obj.status, Icons.SCHEDULE)
        variant = variant_map.get(obj.status, 'warning')
        text = obj.get_status_display() if hasattr(obj, 'get_status_display') else obj.status.title()
        return self.html.badge(text, variant=variant, icon=icon)

    @computed_field("Approved By")
    def approved_by_display(self, obj: ApprovalLog) -> str:
        """Approved by user display."""
        if not obj.approved_by:
            return "—"
        # Simple username display, UserField handles avatar and styling
        return obj.approved_by.username

    @computed_field("Decision Time")
    def decision_time_display(self, obj: ApprovalLog) -> str:
        """Decision time display."""
        if obj.decision_time:
            return f"{obj.decision_time:.2f}s"
        return "—"

    @computed_field("Expires")
    def expires_at_display(self, obj: ApprovalLog) -> str:
        """Expiry time with relative display."""
        if not obj.expires_at:
            return "—"

        # DateTimeField in display_fields handles formatting automatically
        return obj.expires_at


# ===== Toolset Configuration Admin Config =====

toolset_config_config = AdminConfig(
    model=ToolsetConfiguration,

    # Performance optimization
    select_related=['created_by'],

    # Import/Export
    import_export_enabled=True,

    # List display
    list_display=[
        'name_display',
        'toolset_class_display',
        'status_display',
        'usage_count_display',
        'created_by_display',
        'created_at_display'
    ],

    # Display fields with UI widgets
    display_fields=[
        BadgeField(
            name="name",
            title="Configuration Name",
            variant="primary",
            icon=Icons.SETTINGS,
            header=True
        ),
        BadgeField(
            name="toolset_class",
            title="Toolset Class",
            variant="info",
            icon=Icons.EXTENSION
        ),
        BadgeField(
            name="is_active",
            title="Status"
        ),
        TextField(
            name="usage_count",
            title="Usage"
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
    search_fields=['name', 'description', 'toolset_class'],
    list_filter=[
        'is_active',
        'toolset_class',
        'created_at',
        ('created_by', AutocompleteSelectFilter)
    ],

    # List display links
    list_display_links=['name_display'],

    # Autocomplete fields
    autocomplete_fields=['created_by'],

    # Form field overrides
    formfield_overrides={
        models.TextField: {"widget": WysiwygWidget},
        JSONField: {"widget": JSONEditorWidget},
    },

    # Actions
    actions=[
        ActionConfig(
            name="activate_configurations",
            description="Activate configurations",
            variant="success",
            icon=Icons.CHECK_CIRCLE,
            handler=activate_configurations
        ),
        ActionConfig(
            name="deactivate_configurations",
            description="Deactivate configurations",
            variant="warning",
            icon=Icons.PAUSE_CIRCLE,
            handler=deactivate_configurations
        ),
        ActionConfig(
            name="reset_usage",
            description="Reset usage count",
            variant="primary",
            icon=Icons.REFRESH,
            handler=reset_usage
        ),
    ],

    # Ordering
    ordering=['-created_at'],
)


@admin.register(ToolsetConfiguration)
class ToolsetConfigurationAdmin(PydanticAdmin):
    """
    Toolset Configuration admin using NEW Pydantic declarative approach.

    Features:
    - Declarative configuration with type safety
    - Automatic display method generation
    - Material Icons integration
    - Export functionality (via config)
    - Configuration management actions
    """
    config = toolset_config_config

    # Readonly fields
    readonly_fields = ['id', 'created_at', 'updated_at']

    # Fieldsets
    fieldsets = [
        FieldsetConfig(
            title="Configuration Info",
            fields=['name', 'description', 'toolset_class']
        ),
        FieldsetConfig(
            title="Settings",
            fields=['configuration', 'is_active']
        ),
        FieldsetConfig(
            title="Usage",
            fields=['usage_count']
        ),
        FieldsetConfig(
            title="Metadata",
            fields=['created_by', 'updated_by', 'created_at', 'updated_at'],
            collapsed=True
        ),
    ]

    # Custom display methods using @computed_field decorator
    @computed_field("Configuration Name")
    def name_display(self, obj: ToolsetConfiguration) -> str:
        """Enhanced configuration name display."""
        return self.html.badge(obj.name, variant="primary", icon=Icons.SETTINGS)

    @computed_field("Toolset Class")
    def toolset_class_display(self, obj: ToolsetConfiguration) -> str:
        """Toolset class display with badge."""
        if not obj.toolset_class:
            return "—"

        # Extract class name from full path
        class_name = obj.toolset_class.split('.')[-1] if '.' in obj.toolset_class else obj.toolset_class

        return self.html.badge(class_name, variant="info", icon=Icons.EXTENSION)

    @computed_field("Status")
    def status_display(self, obj: ToolsetConfiguration) -> str:
        """Status display based on active state."""
        if obj.is_active:
            return self.html.badge("Active", variant="success", icon=Icons.CHECK_CIRCLE)
        else:
            return self.html.badge("Inactive", variant="secondary", icon=Icons.PAUSE_CIRCLE)

    @computed_field("Usage")
    def usage_count_display(self, obj: ToolsetConfiguration) -> str:
        """Usage count display."""
        if not obj.usage_count:
            return "Not used"
        return f"{obj.usage_count} times"

    @computed_field("Created By")
    def created_by_display(self, obj: ToolsetConfiguration) -> str:
        """Created by user display."""
        if not obj.created_by:
            return "—"
        # Simple username display, UserField handles avatar and styling
        return obj.created_by.username

    @computed_field("Created")
    def created_at_display(self, obj: ToolsetConfiguration) -> str:
        """Created time with relative display."""
        # DateTimeField in display_fields handles formatting automatically
        return obj.created_at
