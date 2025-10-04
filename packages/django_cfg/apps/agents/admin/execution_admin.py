"""
Execution admin interfaces using Django Admin Utilities.

Enhanced execution management with Material Icons and optimized queries.
"""

from django.contrib import admin, messages
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db import models
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from django.db.models.fields.json import JSONField
from datetime import timedelta
from django_json_widget.widgets import JSONEditorWidget
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import AutocompleteSelectFilter, AutocompleteSelectMultipleFilter
from unfold.contrib.forms.widgets import WysiwygWidget
from django_cfg import ExportMixin, ExportForm

from django_cfg.modules.django_admin import (
    OptimizedModelAdmin,
    DisplayMixin,
    MoneyDisplayConfig,
    StatusBadgeConfig,
    DateTimeDisplayConfig,
    Icons,
    ActionVariant,
    display,
    action
)
from django_cfg.modules.django_admin.utils.badges import StatusBadge

from ..models.execution import AgentExecution, WorkflowExecution


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
    
    @display(description="Status")
    def status_badge_inline(self, obj):
        """Status badge for inline display."""
        status_config = StatusBadgeConfig(
            custom_mappings={
                'pending': 'warning',
                'running': 'info', 
                'completed': 'success',
                'failed': 'danger',
                'cancelled': 'secondary'
            },
            show_icons=True,
            icon=Icons.PLAY_ARROW
        )
        return self.display_status_auto(obj, 'status', status_config)
    
    @display(description="Execution Time")
    def execution_time_display(self, obj):
        """Execution time display for inline."""
        if obj.execution_time:
            return f"{obj.execution_time:.2f}s"
        return "—"
    
    @display(description="Cost")
    def cost_display_inline(self, obj):
        """Cost display for inline."""
        if obj.cost:
            config = MoneyDisplayConfig(currency="USD", show_sign=False)
            return self.display_money_amount(obj, 'cost', config)
        return "—"
    
    def get_queryset(self, request):
        """Optimize queryset for inline display."""
        return super().get_queryset(request).select_related('user').order_by('execution_order')


@admin.register(AgentExecution)
class AgentExecutionAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin, ExportMixin):
    """Enhanced admin for AgentExecution model using Django Admin Utilities."""
    
    # Performance optimization
    select_related_fields = ['user', 'workflow_execution', 'agent_definition']
    
    # Export-only configuration
    export_form_class = ExportForm
    
    list_display = [
        'id_display', 'agent_name_display', 'status_display', 'user_display', 
        'execution_time_display', 'tokens_display', 'cost_display', 'cached_display', 'created_at_display'
    ]
    list_display_links = ['id_display', 'agent_name_display']
    list_filter = [
        'status', 'cached', 'agent_name', 'created_at',
        ('user', AutocompleteSelectFilter),
        ('workflow_execution', AutocompleteSelectFilter)
    ]
    search_fields = ['agent_name', 'user__username', 'input_prompt', 'output_data']
    autocomplete_fields = ['user', 'workflow_execution', 'agent_definition']
    readonly_fields = [
        'id', 'execution_time', 'tokens_used', 'cost', 'cached',
        'created_at', 'started_at', 'completed_at', 'duration_display',
        'input_preview', 'output_preview', 'error_preview'
    ]
    ordering = ['-created_at']
    
    # Unfold form field overrides
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
        JSONField: {"widget": JSONEditorWidget},
    }
    
    fieldsets = (
        ("🚀 Execution Info", {
            'fields': ('id', 'agent_name', 'agent_definition', 'user', 'status'),
            'classes': ('tab',)
        }),
        ("📝 Input/Output", {
            'fields': ('input_preview', 'input_prompt', 'output_preview', 'output_data', 'error_preview', 'error_message'),
            'classes': ('tab',)
        }),
        ("📊 Metrics", {
            'fields': ('execution_time', 'tokens_used', 'cost', 'cached'),
            'classes': ('tab',)
        }),
        ("🔗 Workflow Context", {
            'fields': ('workflow_execution', 'execution_order'),
            'classes': ('tab', 'collapse')
        }),
        ("⏰ Timestamps", {
            'fields': ('created_at', 'started_at', 'completed_at', 'duration_display'),
            'classes': ('tab', 'collapse')
        }),
    )
    
    actions = ['retry_failed_executions', 'clear_cache']
    
    @display(description="ID")
    def id_display(self, obj):
        """Enhanced ID display."""
        config = StatusBadgeConfig(show_icons=True, icon=Icons.TAG)
        return StatusBadge.create(
            text=f"#{str(obj.id)[:8]}",
            variant="secondary",
            config=config
        )
    
    @display(description="Agent")
    def agent_name_display(self, obj):
        """Enhanced agent name display."""
        config = StatusBadgeConfig(show_icons=True, icon=Icons.SMART_TOY)
        return StatusBadge.create(
            text=obj.agent_name,
            variant="primary",
            config=config
        )
    
    @display(description="Status")
    def status_display(self, obj):
        """Status display with appropriate icons."""
        status_config = StatusBadgeConfig(
            custom_mappings={
                'pending': 'warning',
                'running': 'info', 
                'completed': 'success',
                'failed': 'danger',
                'cancelled': 'secondary'
            },
            show_icons=True,
            icon=Icons.PLAY_ARROW if obj.status == 'running' else Icons.CHECK_CIRCLE if obj.status == 'completed' else Icons.ERROR if obj.status == 'failed' else Icons.SCHEDULE
        )
        return self.display_status_auto(obj, 'status', status_config)
    
    @display(description="User")
    def user_display(self, obj):
        """User display with avatar."""
        if not obj.user:
            return "—"
        return self.display_user_simple(obj.user)
    
    @display(description="Time")
    def execution_time_display(self, obj):
        """Execution time display."""
        if obj.execution_time:
            return f"{obj.execution_time:.2f}s"
        return "—"
    
    @display(description="Tokens")
    def tokens_display(self, obj):
        """Tokens display."""
        if obj.tokens_used:
            return f"{obj.tokens_used:,}"
        return "—"
    
    @display(description="Cost")
    def cost_display(self, obj):
        """Cost display with formatting."""
        if obj.cost:
            config = MoneyDisplayConfig(
                currency="USD",
                show_sign=False,
                smart_decimal_places=True
            )
            return self.display_money_amount(obj, 'cost', config)
        return "—"
    
    @display(description="Cached", boolean=True)
    def cached_display(self, obj):
        """Cached status display."""
        return obj.cached
    
    @display(description="Created")
    def created_at_display(self, obj):
        """Created time with relative display."""
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'created_at', config)
    
    @display(description="Duration")
    def duration_display(self, obj):
        """Display execution duration."""
        if obj.duration:
            return f"{obj.duration:.2f}s"
        return "—"
    
    @display(description="Input Preview")
    def input_preview(self, obj):
        """Preview of input prompt."""
        if not obj.input_prompt:
            return "—"
        return obj.input_prompt[:200] + "..." if len(obj.input_prompt) > 200 else obj.input_prompt
    
    @display(description="Output Preview")
    def output_preview(self, obj):
        """Preview of output data."""
        if not obj.output_data:
            return "—"
        return str(obj.output_data)[:200] + "..." if len(str(obj.output_data)) > 200 else str(obj.output_data)
    
    @display(description="Error Preview")
    def error_preview(self, obj):
        """Preview of error message."""
        if not obj.error_message:
            return "—"
        return obj.error_message[:200] + "..." if len(obj.error_message) > 200 else obj.error_message
    
    @action(description="Retry failed executions", variant=ActionVariant.WARNING)
    def retry_failed_executions(self, request, queryset):
        """Retry failed executions."""
        failed_count = queryset.filter(status='failed').count()
        messages.warning(request, f"Retry functionality not implemented yet. {failed_count} failed executions selected.")
    
    @action(description="Clear cache", variant=ActionVariant.INFO)
    def clear_cache(self, request, queryset):
        """Clear cache for selected executions."""
        cached_count = queryset.filter(cached=True).count()
        messages.info(request, f"Cache clearing not implemented yet. {cached_count} cached executions selected.")


@admin.register(WorkflowExecution)
class WorkflowExecutionAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin, ExportMixin):
    """Enhanced admin for WorkflowExecution model using Django Admin Utilities."""
    
    # Performance optimization
    select_related_fields = ['user']
    
    # Export-only configuration
    export_form_class = ExportForm
    
    list_display = [
        'id_display', 'name_display', 'pattern_display', 'status_display', 'user_display',
        'progress_display', 'total_time_display', 'total_tokens_display', 'cost_display', 'created_at_display'
    ]
    list_display_links = ['id_display', 'name_display']
    list_filter = [
        'status', 'pattern', 'created_at',
        ('user', AutocompleteSelectFilter)
    ]
    search_fields = ['name', 'user__username', 'input_prompt', 'final_output']
    autocomplete_fields = ['user']
    readonly_fields = [
        'id', 'total_execution_time', 'total_tokens_used', 'total_cost',
        'created_at', 'started_at', 'completed_at', 'duration_display', 
        'progress_percentage', 'input_preview', 'output_preview', 'error_preview'
    ]
    ordering = ['-created_at']
    inlines = [AgentExecutionInlineForWorkflow]
    
    # Unfold form field overrides
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
        JSONField: {"widget": JSONEditorWidget},
    }
    
    fieldsets = (
        ("🔄 Workflow Info", {
            'fields': ('id', 'name', 'user', 'pattern', 'status'),
            'classes': ('tab',)
        }),
        ("⚙️ Configuration", {
            'fields': ('agent_names', 'input_preview', 'input_prompt', 'config'),
            'classes': ('tab',)
        }),
        ("📈 Progress", {
            'fields': ('current_step', 'total_steps', 'progress_percentage'),
            'classes': ('tab',)
        }),
        ("📋 Results", {
            'fields': ('output_preview', 'final_output', 'error_preview', 'error_message'),
            'classes': ('tab',)
        }),
        ("📊 Metrics", {
            'fields': ('total_execution_time', 'total_tokens_used', 'total_cost'),
            'classes': ('tab',)
        }),
        ("⏰ Timestamps", {
            'fields': ('created_at', 'started_at', 'completed_at', 'duration_display'),
            'classes': ('tab', 'collapse')
        }),
    )
    
    actions = ['cancel_running_workflows', 'retry_failed_workflows']
    
    @display(description="ID")
    def id_display(self, obj):
        """Enhanced ID display."""
        config = StatusBadgeConfig(show_icons=True, icon=Icons.TAG)
        return StatusBadge.create(
            text=f"#{str(obj.id)[:8]}",
            variant="secondary",
            config=config
        )
    
    @display(description="Workflow")
    def name_display(self, obj):
        """Enhanced workflow name display."""
        config = StatusBadgeConfig(show_icons=True, icon=Icons.ACCOUNT_TREE)
        return StatusBadge.create(
            text=obj.name,
            variant="primary",
            config=config
        )
    
    @display(description="Pattern")
    def pattern_display(self, obj):
        """Pattern display with appropriate icons."""
        pattern_config = StatusBadgeConfig(
            custom_mappings={
                'sequential': 'info',
                'parallel': 'success',
                'conditional': 'warning',
                'loop': 'secondary'
            },
            show_icons=True,
            icon=Icons.LINEAR_SCALE if obj.pattern == 'sequential' else Icons.CALL_SPLIT if obj.pattern == 'parallel' else Icons.DEVICE_HUB if obj.pattern == 'conditional' else Icons.LOOP
        )
        return self.display_status_auto(
            type('obj', (), {'pattern': obj.pattern.title() if obj.pattern else 'Unknown'})(),
            'pattern',
            pattern_config
        )
    
    @display(description="Status")
    def status_display(self, obj):
        """Status display with appropriate icons."""
        status_config = StatusBadgeConfig(
            custom_mappings={
                'pending': 'warning',
                'running': 'info', 
                'completed': 'success',
                'failed': 'danger',
                'cancelled': 'secondary'
            },
            show_icons=True,
            icon=Icons.PLAY_ARROW if obj.status == 'running' else Icons.CHECK_CIRCLE if obj.status == 'completed' else Icons.ERROR if obj.status == 'failed' else Icons.SCHEDULE
        )
        return self.display_status_auto(obj, 'status', status_config)
    
    @display(description="User")
    def user_display(self, obj):
        """User display with avatar."""
        if not obj.user:
            return "—"
        return self.display_user_simple(obj.user)
    
    @display(description="Progress")
    def progress_display(self, obj):
        """Display progress percentage."""
        return f"{int(obj.progress_percentage)}%"
    
    @display(description="Time")
    def total_time_display(self, obj):
        """Total execution time display."""
        if obj.total_execution_time:
            return f"{obj.total_execution_time:.2f}s"
        return "—"
    
    @display(description="Tokens")
    def total_tokens_display(self, obj):
        """Total tokens display."""
        if obj.total_tokens_used:
            return f"{obj.total_tokens_used:,}"
        return "—"
    
    @display(description="Cost")
    def cost_display(self, obj):
        """Cost display with formatting."""
        if obj.total_cost:
            config = MoneyDisplayConfig(
                currency="USD",
                show_sign=False,
                smart_decimal_places=True
            )
            return self.display_money_amount(obj, 'total_cost', config)
        return "—"
    
    @display(description="Created")
    def created_at_display(self, obj):
        """Created time with relative display."""
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'created_at', config)
    
    @display(description="Duration")
    def duration_display(self, obj):
        """Display workflow duration."""
        if obj.duration:
            return f"{obj.duration:.2f}s"
        return "—"
    
    @display(description="Input Preview")
    def input_preview(self, obj):
        """Preview of input prompt."""
        if not obj.input_prompt:
            return "—"
        return obj.input_prompt[:200] + "..." if len(obj.input_prompt) > 200 else obj.input_prompt
    
    @display(description="Output Preview")
    def output_preview(self, obj):
        """Preview of final output."""
        if not obj.final_output:
            return "—"
        return str(obj.final_output)[:200] + "..." if len(str(obj.final_output)) > 200 else str(obj.final_output)
    
    @display(description="Error Preview")
    def error_preview(self, obj):
        """Preview of error message."""
        if not obj.error_message:
            return "—"
        return obj.error_message[:200] + "..." if len(obj.error_message) > 200 else obj.error_message
    
    @action(description="Cancel running workflows", variant=ActionVariant.DANGER)
    def cancel_running_workflows(self, request, queryset):
        """Cancel running workflows."""
        running_count = queryset.filter(status='running').count()
        messages.warning(request, f"Cancel functionality not implemented yet. {running_count} running workflows selected.")
    
    @action(description="Retry failed workflows", variant=ActionVariant.WARNING)
    def retry_failed_workflows(self, request, queryset):
        """Retry failed workflows."""
        failed_count = queryset.filter(status='failed').count()
        messages.warning(request, f"Retry functionality not implemented yet. {failed_count} failed workflows selected.")