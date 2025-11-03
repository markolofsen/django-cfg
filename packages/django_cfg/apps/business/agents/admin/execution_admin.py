"""
Execution Admin v2.0 - NEW Declarative Pydantic Approach

Enhanced execution management with Material Icons and clean declarative config.
"""

from django.contrib import admin
from django.db import models
from django.db.models.fields.json import JSONField
from django_json_widget.widgets import JSONEditorWidget
from unfold.admin import ModelAdmin, TabularInline
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

from ..models.execution import AgentExecution, WorkflowExecution
from .execution_actions import (
    retry_failed_executions,
    clear_cache,
    cancel_running_workflows,
    retry_failed_workflows,
)


# ===== Agent Execution Inline =====

class AgentExecutionInlineForWorkflow(TabularInline):
    """Enhanced inline for agent executions within workflow."""

    model = AgentExecution
    verbose_name = "Agent Execution"
    verbose_name_plural = "🔗 Workflow Steps"
    extra = 0
    max_num = 0
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    fields = [
        'execution_order', 'agent_name', 'status_badge_inline',
        'execution_time_display', 'tokens_used', 'cost_display_inline'
    ]
    readonly_fields = [
        'execution_order', 'agent_name', 'status_badge_inline',
        'execution_time_display', 'tokens_used', 'cost_display_inline'
    ]

    # Unfold specific options
    hide_title = False
    classes = ['collapse']

    @computed_field("Status")
    def status_badge_inline(self, obj):
        """Status badge for inline display."""
        status_variants = {
            'pending': 'warning',
            'running': 'info',
            'completed': 'success',
            'failed': 'danger',
            'cancelled': 'secondary'
        }

        icon_map = {
            'running': Icons.PLAY_ARROW,
            'completed': Icons.CHECK_CIRCLE,
            'failed': Icons.ERROR,
            'pending': Icons.SCHEDULE,
            'cancelled': Icons.CANCEL
        }

        icon = icon_map.get(obj.status, Icons.SCHEDULE)
        variant = status_variants.get(obj.status, 'secondary')

        # Note: self.html is not available in inline context
        # We'll use a simple HTML string for now
        from django.utils.html import format_html
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            variant,
            obj.get_status_display() if hasattr(obj, 'get_status_display') else obj.status
        )

    @computed_field("Execution Time")
    def execution_time_display(self, obj):
        """Execution time display for inline."""
        if obj.execution_time:
            return f"{obj.execution_time:.2f}s"
        return "—"

    @computed_field("Cost")
    def cost_display_inline(self, obj):
        """Cost display for inline."""
        if obj.cost:
            return f"${obj.cost:.2f}"
        return "—"

    def get_queryset(self, request):
        """Optimize queryset for inline display."""
        return super().get_queryset(request).select_related('user').order_by('execution_order')


# ===== Agent Execution Admin Config =====

agent_execution_config = AdminConfig(
    model=AgentExecution,

    # Performance optimization
    select_related=['user', 'workflow_execution', 'agent_definition'],

    # Import/Export
    import_export_enabled=True,

    # List display
    list_display=[
        'id_display',
        'agent_name_display',
        'status_display',
        'user_display',
        'execution_time_display',
        'tokens_display',
        'cost_display',
        'cached_display',
        'created_at_display'
    ],

    # Display fields with UI widgets
    display_fields=[
        BadgeField(
            name="id",
            title="ID",
            variant="secondary",
            icon=Icons.TAG
        ),
        BadgeField(
            name="agent_name",
            title="Agent",
            variant="primary",
            icon=Icons.SMART_TOY,
            header=True
        ),
        BadgeField(
            name="status",
            title="Status"
        ),
        UserField(
            name="user",
            title="User"
        ),
        DateTimeField(
            name="created_at",
            title="Created",
            ordering="created_at"
        ),
    ],

    # Search and filters
    search_fields=["agent_name", "user__username", "input_prompt", "output_data"],
    list_filter=[
        "status",
        "cached",
        "agent_name",
        "created_at",
        ("user", AutocompleteSelectFilter),
        ("workflow_execution", AutocompleteSelectFilter)
    ],

    # Ordering
    ordering=["-created_at"],

    # List display links
    list_display_links=['id_display', 'agent_name_display'],

    # Autocomplete fields
    autocomplete_fields=['user', 'workflow_execution', 'agent_definition'],

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
            name="clear_cache",
            description="Clear cache",
            variant="primary",
            icon=Icons.DELETE,
            handler=clear_cache
        ),
    ],
)


@admin.register(AgentExecution)
class AgentExecutionAdmin(PydanticAdmin):
    """
    Agent Execution admin using NEW Pydantic declarative approach.

    Features:
    - Declarative configuration with type safety
    - Automatic display method generation
    - Material Icons integration
    - Export functionality (via config)
    - Custom actions for execution management
    """
    config = agent_execution_config

    # Readonly fields
    readonly_fields = [
        'id', 'execution_time', 'tokens_used', 'cost', 'cached',
        'created_at', 'started_at', 'completed_at', 'duration_display',
        'input_preview', 'output_preview', 'error_preview'
    ]

    # Fieldsets
    fieldsets = [
        FieldsetConfig(
            title="Execution Info",
            fields=['agent_name', 'agent_definition', 'status']
        ),
        FieldsetConfig(
            title="Input/Output",
            fields=['input_preview', 'input_prompt', 'output_preview', 'output_data', 'error_preview', 'error_message']
        ),
        FieldsetConfig(
            title="Metrics",
            fields=['execution_time', 'tokens_used', 'cost', 'cached']
        ),
        FieldsetConfig(
            title="Workflow Context",
            fields=['workflow_execution', 'execution_order'],
            collapsed=True
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=['created_at', 'started_at', 'completed_at', 'duration_display'],
            collapsed=True
        ),
    ]

    # Pagination
    list_per_page = 50

    # Custom display methods using @computed_field decorator
    @computed_field("ID")
    def id_display(self, obj: AgentExecution) -> str:
        """Enhanced ID display."""
        return self.html.badge(
            f"#{str(obj.id)[:8]}",
            variant="secondary",
            icon=Icons.TAG
        )

    @computed_field("Agent")
    def agent_name_display(self, obj: AgentExecution) -> str:
        """Enhanced agent name display."""
        return self.html.badge(
            obj.agent_name,
            variant="primary",
            icon=Icons.SMART_TOY
        )

    @computed_field("Status")
    def status_display(self, obj: AgentExecution) -> str:
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
        variant = variant_map.get(obj.status, 'secondary')

        return self.html.badge(
            obj.get_status_display() if hasattr(obj, 'get_status_display') else obj.status,
            variant=variant,
            icon=icon
        )

    @computed_field("User")
    def user_display(self, obj: AgentExecution) -> str:
        """User display with avatar."""
        if not obj.user:
            return "—"
        # Simple username display, UserField handles avatar and styling
        return obj.user.username

    @computed_field("Time")
    def execution_time_display(self, obj: AgentExecution) -> str:
        """Execution time display."""
        if obj.execution_time:
            return f"{obj.execution_time:.2f}s"
        return "—"

    @computed_field("Tokens")
    def tokens_display(self, obj: AgentExecution) -> str:
        """Tokens display."""
        if obj.tokens_used:
            return f"{obj.tokens_used:,}"
        return "—"

    @computed_field("Cost")
    def cost_display(self, obj: AgentExecution) -> str:
        """Cost display with formatting."""
        if obj.cost:
            # Smart decimal places: show more decimals for small amounts
            if obj.cost < 0.01:
                return f"${obj.cost:.6f}"
            elif obj.cost < 1:
                return f"${obj.cost:.4f}"
            else:
                return f"${obj.cost:.2f}"
        return "—"

    @computed_field("Cached", boolean=True)
    def cached_display(self, obj: AgentExecution) -> bool:
        """Cached status display."""
        return obj.cached

    @computed_field("Created")
    def created_at_display(self, obj: AgentExecution) -> str:
        """Created time with relative display."""
        # DateTimeField in display_fields handles formatting automatically
        return obj.created_at

    @computed_field("Duration")
    def duration_display(self, obj: AgentExecution) -> str:
        """Display execution duration."""
        if obj.duration:
            return f"{obj.duration:.2f}s"
        return "—"

    @computed_field("Input Preview")
    def input_preview(self, obj: AgentExecution) -> str:
        """Preview of input prompt."""
        if not obj.input_prompt:
            return "—"
        return obj.input_prompt[:200] + "..." if len(obj.input_prompt) > 200 else obj.input_prompt

    @computed_field("Output Preview")
    def output_preview(self, obj: AgentExecution) -> str:
        """Preview of output data."""
        if not obj.output_data:
            return "—"
        return str(obj.output_data)[:200] + "..." if len(str(obj.output_data)) > 200 else str(obj.output_data)

    @computed_field("Error Preview")
    def error_preview(self, obj: AgentExecution) -> str:
        """Preview of error message."""
        if not obj.error_message:
            return "—"
        return obj.error_message[:200] + "..." if len(obj.error_message) > 200 else obj.error_message


# ===== Workflow Execution Admin Config =====

workflow_execution_config = AdminConfig(
    model=WorkflowExecution,

    # Performance optimization
    select_related=['user'],

    # Import/Export
    import_export_enabled=True,

    # List display
    list_display=[
        'id_display',
        'name_display',
        'pattern_display',
        'status_display',
        'user_display',
        'progress_display',
        'total_time_display',
        'total_tokens_display',
        'cost_display',
        'created_at_display'
    ],

    # Display fields with UI widgets
    display_fields=[
        BadgeField(
            name="id",
            title="ID",
            variant="secondary",
            icon=Icons.TAG
        ),
        BadgeField(
            name="name",
            title="Workflow",
            variant="primary",
            icon=Icons.ACCOUNT_TREE,
            header=True
        ),
        BadgeField(
            name="pattern",
            title="Pattern",
            variant="info",
            icon=Icons.LINEAR_SCALE
        ),
        BadgeField(
            name="status",
            title="Status"
        ),
        UserField(
            name="user",
            title="User"
        ),
        DateTimeField(
            name="created_at",
            title="Created",
            ordering="created_at"
        ),
    ],

    # Search and filters
    search_fields=["name", "user__username", "input_prompt", "final_output"],
    list_filter=[
        "status",
        "pattern",
        "created_at",
        ("user", AutocompleteSelectFilter)
    ],

    # List display links
    list_display_links=['id_display', 'name_display'],

    # Autocomplete fields
    autocomplete_fields=['user'],

    # Form field overrides
    formfield_overrides={
        models.TextField: {"widget": WysiwygWidget},
        JSONField: {"widget": JSONEditorWidget},
    },

    # Actions
    actions=[
        ActionConfig(
            name="cancel_running_workflows",
            description="Cancel running workflows",
            variant="danger",
            icon=Icons.CANCEL,
            confirmation=True,
            handler=cancel_running_workflows
        ),
        ActionConfig(
            name="retry_failed_workflows",
            description="Retry failed workflows",
            variant="warning",
            icon=Icons.REFRESH,
            handler=retry_failed_workflows
        ),
    ],

    # Ordering
    ordering=["-created_at"],
)


@admin.register(WorkflowExecution)
class WorkflowExecutionAdmin(PydanticAdmin):
    """
    Workflow Execution admin using NEW Pydantic declarative approach.

    Features:
    - Declarative configuration with type safety
    - Automatic display method generation
    - Material Icons integration
    - Export functionality (via config)
    - Inline agent execution display
    - Custom actions for workflow management
    """
    config = workflow_execution_config

    # Readonly fields
    readonly_fields = [
        'id', 'total_execution_time', 'total_tokens_used', 'total_cost',
        'created_at', 'started_at', 'completed_at', 'duration_display',
        'progress_percentage', 'input_preview', 'output_preview', 'error_preview'
    ]

    # Inlines
    inlines = [AgentExecutionInlineForWorkflow]

    # Fieldsets
    fieldsets = [
        FieldsetConfig(
            title="Workflow Info",
            fields=['name', 'pattern', 'status']
        ),
        FieldsetConfig(
            title="Configuration",
            fields=['agent_names', 'input_preview', 'input_prompt', 'config']
        ),
        FieldsetConfig(
            title="Progress",
            fields=['current_step', 'total_steps', 'progress_percentage']
        ),
        FieldsetConfig(
            title="Results",
            fields=['output_preview', 'final_output', 'error_preview', 'error_message']
        ),
        FieldsetConfig(
            title="Metrics",
            fields=['total_execution_time', 'total_tokens_used', 'total_cost']
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=['created_at', 'started_at', 'completed_at', 'duration_display'],
            collapsed=True
        ),
    ]

    # Pagination
    list_per_page = 50

    # Custom display methods using @computed_field decorator
    @computed_field("ID")
    def id_display(self, obj: WorkflowExecution) -> str:
        """Enhanced ID display."""
        return self.html.badge(
            f"#{str(obj.id)[:8]}",
            variant="secondary",
            icon=Icons.TAG
        )

    @computed_field("Workflow")
    def name_display(self, obj: WorkflowExecution) -> str:
        """Enhanced workflow name display."""
        return self.html.badge(
            obj.name,
            variant="primary",
            icon=Icons.ACCOUNT_TREE
        )

    @computed_field("Pattern")
    def pattern_display(self, obj: WorkflowExecution) -> str:
        """Pattern display with appropriate icons."""
        pattern_icons = {
            'sequential': Icons.LINEAR_SCALE,
            'parallel': Icons.CALL_SPLIT,
            'conditional': Icons.DEVICE_HUB,
            'loop': Icons.LOOP
        }

        pattern_variants = {
            'sequential': 'info',
            'parallel': 'success',
            'conditional': 'warning',
            'loop': 'secondary'
        }

        icon = pattern_icons.get(obj.pattern, Icons.LINEAR_SCALE)
        variant = pattern_variants.get(obj.pattern, 'info')

        return self.html.badge(
            obj.pattern.title() if obj.pattern else 'Unknown',
            variant=variant,
            icon=icon
        )

    @computed_field("Status")
    def status_display(self, obj: WorkflowExecution) -> str:
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
        variant = variant_map.get(obj.status, 'secondary')

        return self.html.badge(
            obj.get_status_display() if hasattr(obj, 'get_status_display') else obj.status,
            variant=variant,
            icon=icon
        )

    @computed_field("User")
    def user_display(self, obj: WorkflowExecution) -> str:
        """User display with avatar."""
        if not obj.user:
            return "—"
        # Simple username display, UserField handles avatar and styling
        return obj.user.username

    @computed_field("Progress")
    def progress_display(self, obj: WorkflowExecution) -> str:
        """Display progress percentage."""
        return f"{int(obj.progress_percentage)}%"

    @computed_field("Time")
    def total_time_display(self, obj: WorkflowExecution) -> str:
        """Total execution time display."""
        if obj.total_execution_time:
            return f"{obj.total_execution_time:.2f}s"
        return "—"

    @computed_field("Tokens")
    def total_tokens_display(self, obj: WorkflowExecution) -> str:
        """Total tokens display."""
        if obj.total_tokens_used:
            return f"{obj.total_tokens_used:,}"
        return "—"

    @computed_field("Cost")
    def cost_display(self, obj: WorkflowExecution) -> str:
        """Cost display with formatting."""
        if obj.total_cost:
            # Smart decimal places: show more decimals for small amounts
            if obj.total_cost < 0.01:
                return f"${obj.total_cost:.6f}"
            elif obj.total_cost < 1:
                return f"${obj.total_cost:.4f}"
            else:
                return f"${obj.total_cost:.2f}"
        return "—"

    @computed_field("Created")
    def created_at_display(self, obj: WorkflowExecution) -> str:
        """Created time with relative display."""
        # DateTimeField in display_fields handles formatting automatically
        return obj.created_at

    @computed_field("Duration")
    def duration_display(self, obj: WorkflowExecution) -> str:
        """Display workflow duration."""
        if obj.duration:
            return f"{obj.duration:.2f}s"
        return "—"

    @computed_field("Input Preview")
    def input_preview(self, obj: WorkflowExecution) -> str:
        """Preview of input prompt."""
        if not obj.input_prompt:
            return "—"
        return obj.input_prompt[:200] + "..." if len(obj.input_prompt) > 200 else obj.input_prompt

    @computed_field("Output Preview")
    def output_preview(self, obj: WorkflowExecution) -> str:
        """Preview of final output."""
        if not obj.final_output:
            return "—"
        return str(obj.final_output)[:200] + "..." if len(str(obj.final_output)) > 200 else str(obj.final_output)

    @computed_field("Error Preview")
    def error_preview(self, obj: WorkflowExecution) -> str:
        """Preview of error message."""
        if not obj.error_message:
            return "—"
        return obj.error_message[:200] + "..." if len(obj.error_message) > 200 else obj.error_message
