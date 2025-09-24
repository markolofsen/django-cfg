"""
Execution admin interfaces with Unfold optimization.
"""

from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db import models
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from django.db.models.fields.json import JSONField
from datetime import timedelta
from django_json_widget.widgets import JSONEditorWidget
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display, action
from unfold.enums import ActionVariant
from unfold.contrib.filters.admin import AutocompleteSelectFilter, AutocompleteSelectMultipleFilter
from unfold.contrib.forms.widgets import WysiwygWidget
from django_cfg import ExportMixin, ExportForm

from ..models.execution import AgentExecution, WorkflowExecution


class AgentExecutionInlineForWorkflow(TabularInline):
    """Inline for agent executions within workflow with Unfold styling."""
    
    model = AgentExecution
    verbose_name = "Agent Execution"
    verbose_name_plural = "🔗 Workflow Steps (Read-only)"
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
        colors = {
            'pending': 'bg-yellow-100 text-yellow-800',
            'running': 'bg-blue-100 text-blue-800', 
            'completed': 'bg-green-100 text-green-800',
            'failed': 'bg-red-100 text-red-800',
            'cancelled': 'bg-gray-100 text-gray-800'
        }
        color_class = colors.get(obj.status, 'bg-gray-100 text-gray-800')
        return format_html(
            '<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium {}">{}</span>',
            color_class, obj.get_status_display()
        )
    
    @display(description="Execution Time")
    def execution_time_display(self, obj):
        """Execution time display for inline."""
        if obj.execution_time:
            return f"{obj.execution_time:.2f}s"
        return "-"
    
    @display(description="Cost")
    def cost_display_inline(self, obj):
        """Cost display for inline."""
        if obj.cost:
            return f"${obj.cost:.4f}"
        return "-"
    
    def get_queryset(self, request):
        """Optimize queryset for inline display."""
        return super().get_queryset(request).select_related('user').order_by('execution_order')


@admin.register(AgentExecution)
class AgentExecutionAdmin(ModelAdmin, ExportMixin):
    """Admin interface for AgentExecution with Unfold styling."""
    
    # Export-only configuration
    export_form_class = ExportForm
    
    list_display = [
        'id_display', 'agent_name_display', 'status_badge', 'user', 
        'execution_metrics', 'cost_display', 'cached_badge', 'created_at'
    ]
    ordering = ['-created_at']
    list_filter = [
        'status', 'cached', 'agent_name', 'created_at',
        ('user', AutocompleteSelectFilter),
        ('workflow_execution', AutocompleteSelectFilter)
    ]
    search_fields = ['agent_name', 'user__username', 'input_prompt', 'output_data']
    autocomplete_fields = ['user', 'workflow_execution']
    readonly_fields = [
        'id', 'execution_time', 'tokens_used', 'cost', 'cached',
        'created_at', 'started_at', 'completed_at', 'duration_display',
        'input_preview', 'output_preview', 'error_preview'
    ]
    
    # Unfold form field overrides
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
        JSONField: {"widget": JSONEditorWidget},
    }
    
    fieldsets = (
        ("🚀 Execution Info", {
            'fields': ('id', 'agent_name', 'user', 'status'),
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
        return format_html(
            '<span class="font-mono text-sm text-gray-600">#{}</span>',
            str(obj.id)[:8]
        )
    
    @display(description="Agent")
    def agent_name_display(self, obj):
        """Enhanced agent name display."""
        return format_html(
            '<div class="flex items-center space-x-2">'
            '<span class="text-blue-600 font-medium">{}</span>'
            '</div>',
            obj.agent_name
        )
    
    @display(description="Status")
    def status_badge(self, obj):
        """Status badge with color coding."""
        colors = {
            'pending': 'bg-yellow-100 text-yellow-800',
            'running': 'bg-blue-100 text-blue-800', 
            'completed': 'bg-green-100 text-green-800',
            'failed': 'bg-red-100 text-red-800',
            'cancelled': 'bg-gray-100 text-gray-800'
        }
        color_class = colors.get(obj.status, 'bg-gray-100 text-gray-800')
        return format_html(
            '<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium {}">{}</span>',
            color_class, obj.get_status_display()
        )
    
    @display(description="Metrics")
    def execution_metrics(self, obj):
        """Combined execution metrics."""
        return format_html(
            '<div class="text-sm space-y-1">'
            '<div><span class="font-medium">Time:</span> {}</div>'
            '<div><span class="font-medium">Tokens:</span> {}</div>'
            '</div>',
            f"{obj.execution_time:.2f}s" if obj.execution_time else "-",
            f"{obj.tokens_used:,}" if obj.tokens_used else "-"
        )
    
    @display(description="Cost")
    def cost_display(self, obj):
        """Cost display with formatting."""
        if obj.cost:
            return format_html(
                '<span class="font-mono text-green-600">${:.4f}</span>',
                obj.cost
            )
        return "-"
    
    @display(description="Cached", boolean=True)
    def cached_badge(self, obj):
        """Cached status badge."""
        return obj.cached
    
    @display(description="Duration")
    def duration_display(self, obj):
        """Display execution duration."""
        if obj.duration:
            return f"{obj.duration:.2f}s"
        return "-"
    
    @display(description="Input Preview")
    def input_preview(self, obj):
        """Preview of input prompt."""
        if not obj.input_prompt:
            return "-"
        preview = obj.input_prompt[:200] + "..." if len(obj.input_prompt) > 200 else obj.input_prompt
        return format_html(
            '<div class="text-sm text-gray-600 max-w-md">{}</div>',
            preview
        )
    
    @display(description="Output Preview")
    def output_preview(self, obj):
        """Preview of output data."""
        if not obj.output_data:
            return "-"
        preview = str(obj.output_data)[:200] + "..." if len(str(obj.output_data)) > 200 else str(obj.output_data)
        return format_html(
            '<div class="text-sm text-gray-600 max-w-md">{}</div>',
            preview
        )
    
    @display(description="Error Preview")
    def error_preview(self, obj):
        """Preview of error message."""
        if not obj.error_message:
            return "-"
        preview = obj.error_message[:200] + "..." if len(obj.error_message) > 200 else obj.error_message
        return format_html(
            '<div class="text-sm text-red-600 max-w-md">{}</div>',
            preview
        )
    
    @action(description="Retry failed executions", icon="refresh", variant=ActionVariant.WARNING)
    def retry_failed_executions(self, request, queryset):
        """Retry failed executions."""
        failed_count = queryset.filter(status='failed').count()
        messages.warning(request, f"Retry functionality not implemented yet. {failed_count} failed executions selected.")
    
    @action(description="Clear cache", icon="clear", variant=ActionVariant.INFO)
    def clear_cache(self, request, queryset):
        """Clear cache for selected executions."""
        cached_count = queryset.filter(cached=True).count()
        messages.info(request, f"Cache clearing not implemented yet. {cached_count} cached executions selected.")
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('user', 'workflow_execution')


@admin.register(WorkflowExecution)
class WorkflowExecutionAdmin(ModelAdmin, ExportMixin):
    """Admin interface for WorkflowExecution with Unfold styling."""
    
    # Export-only configuration
    export_form_class = ExportForm
    
    list_display = [
        'id_display', 'name_display', 'pattern_badge', 'status_badge', 'user',
        'progress_display', 'metrics_display', 'cost_display', 'created_at'
    ]
    ordering = ['-created_at']
    inlines = [AgentExecutionInlineForWorkflow]
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
        return format_html(
            '<span class="font-mono text-sm text-gray-600">#{}</span>',
            str(obj.id)[:8]
        )
    
    @display(description="Workflow")
    def name_display(self, obj):
        """Enhanced workflow name display."""
        return format_html(
            '<div class="flex items-center space-x-2">'
            '<span class="text-indigo-600 font-medium">{}</span>'
            '</div>',
            obj.name
        )
    
    @display(description="Pattern")
    def pattern_badge(self, obj):
        """Pattern badge."""
        colors = {
            'sequential': 'bg-blue-100 text-blue-800',
            'parallel': 'bg-green-100 text-green-800',
            'conditional': 'bg-purple-100 text-purple-800',
            'loop': 'bg-orange-100 text-orange-800'
        }
        color_class = colors.get(obj.pattern, 'bg-gray-100 text-gray-800')
        return format_html(
            '<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium {}">{}</span>',
            color_class, obj.pattern.title() if obj.pattern else 'Unknown'
        )
    
    @display(description="Status")
    def status_badge(self, obj):
        """Status badge with color coding."""
        colors = {
            'pending': 'bg-yellow-100 text-yellow-800',
            'running': 'bg-blue-100 text-blue-800', 
            'completed': 'bg-green-100 text-green-800',
            'failed': 'bg-red-100 text-red-800',
            'cancelled': 'bg-gray-100 text-gray-800'
        }
        color_class = colors.get(obj.status, 'bg-gray-100 text-gray-800')
        return format_html(
            '<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium {}">{}</span>',
            color_class, obj.get_status_display()
        )
    
    @display(description="Progress")
    def progress_display(self, obj):
        """Display progress as a progress bar."""
        percentage = obj.progress_percentage
        color_class = 'bg-green-500' if obj.status == 'completed' else 'bg-blue-500' if obj.status == 'running' else 'bg-red-500'
        
        return format_html(
            '<div class="w-24 bg-gray-200 rounded-full h-2">'
            '<div class="h-2 rounded-full {} flex items-center justify-center text-xs text-white" style="width: {}%;">'
            '</div>'
            '</div>'
            '<div class="text-xs text-gray-600 mt-1">{}%</div>',
            color_class, percentage, int(percentage)
        )
    
    @display(description="Metrics")
    def metrics_display(self, obj):
        """Combined metrics display."""
        return format_html(
            '<div class="text-sm space-y-1">'
            '<div><span class="font-medium">Time:</span> {}</div>'
            '<div><span class="font-medium">Tokens:</span> {}</div>'
            '</div>',
            f"{obj.total_execution_time:.2f}s" if obj.total_execution_time else "-",
            f"{obj.total_tokens_used:,}" if obj.total_tokens_used else "-"
        )
    
    @display(description="Cost")
    def cost_display(self, obj):
        """Cost display with formatting."""
        if obj.total_cost:
            return format_html(
                '<span class="font-mono text-green-600">${:.4f}</span>',
                obj.total_cost
            )
        return "-"
    
    @display(description="Duration")
    def duration_display(self, obj):
        """Display workflow duration."""
        if obj.duration:
            return f"{obj.duration:.2f}s"
        return "-"
    
    @display(description="Input Preview")
    def input_preview(self, obj):
        """Preview of input prompt."""
        if not obj.input_prompt:
            return "-"
        preview = obj.input_prompt[:200] + "..." if len(obj.input_prompt) > 200 else obj.input_prompt
        return format_html(
            '<div class="text-sm text-gray-600 max-w-md">{}</div>',
            preview
        )
    
    @display(description="Output Preview")
    def output_preview(self, obj):
        """Preview of final output."""
        if not obj.final_output:
            return "-"
        preview = str(obj.final_output)[:200] + "..." if len(str(obj.final_output)) > 200 else str(obj.final_output)
        return format_html(
            '<div class="text-sm text-gray-600 max-w-md">{}</div>',
            preview
        )
    
    @display(description="Error Preview")
    def error_preview(self, obj):
        """Preview of error message."""
        if not obj.error_message:
            return "-"
        preview = obj.error_message[:200] + "..." if len(obj.error_message) > 200 else obj.error_message
        return format_html(
            '<div class="text-sm text-red-600 max-w-md">{}</div>',
            preview
        )
    
    @action(description="Cancel running workflows", icon="stop", variant=ActionVariant.DANGER)
    def cancel_running_workflows(self, request, queryset):
        """Cancel running workflows."""
        running_count = queryset.filter(status='running').count()
        messages.warning(request, f"Cancel functionality not implemented yet. {running_count} running workflows selected.")
    
    @action(description="Retry failed workflows", icon="refresh", variant=ActionVariant.WARNING)
    def retry_failed_workflows(self, request, queryset):
        """Retry failed workflows."""
        failed_count = queryset.filter(status='failed').count()
        messages.warning(request, f"Retry functionality not implemented yet. {failed_count} failed workflows selected.")
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('user')
