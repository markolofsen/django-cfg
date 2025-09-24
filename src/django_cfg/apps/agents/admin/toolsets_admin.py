"""
Toolsets admin interfaces with Unfold optimization.
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
from django_cfg import ExportMixin, ImportExportModelAdmin, ImportForm, ExportForm

from ..models.toolsets import ToolExecution, ApprovalLog, ToolsetConfiguration


@admin.register(ToolExecution)
class ToolExecutionAdmin(ModelAdmin, ExportMixin):
    """Admin interface for ToolExecution with Unfold styling."""
    
    # Export-only configuration
    export_form_class = ExportForm
    
    list_display = [
        'id_display', 'tool_name_display', 'toolset_badge', 'status_badge', 'user',
        'execution_metrics', 'retry_badge', 'created_at'
    ]
    ordering = ['-created_at']
    list_filter = [
        'status', 'tool_name', 'toolset_name', 'created_at',
        ('user', AutocompleteSelectFilter),
        ('agent_execution', AutocompleteSelectFilter)
    ]
    search_fields = ['tool_name', 'toolset_name', 'user__username', 'arguments', 'result']
    autocomplete_fields = ['user', 'agent_execution']
    readonly_fields = [
        'id', 'execution_time', 'created_at', 'started_at', 'completed_at', 
        'duration_display', 'arguments_preview', 'result_preview', 'error_preview'
    ]
    
    # Unfold form field overrides
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
        JSONField: {"widget": JSONEditorWidget},
    }
    
    fieldsets = (
        ("🛠️ Tool Info", {
            'fields': ('id', 'tool_name', 'toolset_name', 'user', 'status'),
            'classes': ('tab',)
        }),
        ("📝 Execution Data", {
            'fields': ('arguments_preview', 'arguments', 'result_preview', 'result', 'error_preview', 'error_message'),
            'classes': ('tab',)
        }),
        ("📊 Metrics", {
            'fields': ('execution_time', 'retry_count'),
            'classes': ('tab',)
        }),
        ("🔗 Context", {
            'fields': ('agent_execution',),
            'classes': ('tab', 'collapse')
        }),
        ("⏰ Timestamps", {
            'fields': ('created_at', 'started_at', 'completed_at', 'duration_display'),
            'classes': ('tab', 'collapse')
        }),
    )
    
    actions = ['retry_failed_tools', 'clear_errors']
    
    @display(description="ID")
    def id_display(self, obj):
        """Enhanced ID display."""
        return format_html(
            '<span class="font-mono text-sm text-gray-600">#{}</span>',
            str(obj.id)[:8]
        )
    
    @display(description="Tool")
    def tool_name_display(self, obj):
        """Enhanced tool name display."""
        return format_html(
            '<div class="flex items-center space-x-2">'
            '<span class="text-orange-600 font-medium">{}</span>'
            '</div>',
            obj.tool_name
        )
    
    @display(description="Toolset")
    def toolset_badge(self, obj):
        """Toolset badge."""
        if not obj.toolset_name:
            return "-"
        return format_html(
            '<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-amber-100 text-amber-800">{}</span>',
            obj.toolset_name
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
            '</div>',
            f"{obj.execution_time:.3f}s" if obj.execution_time else "-"
        )
    
    @display(description="Retries")
    def retry_badge(self, obj):
        """Retry count badge."""
        if obj.retry_count > 0:
            return format_html(
                '<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">{}</span>',
                obj.retry_count
            )
        return format_html(
            '<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">0</span>'
        )
    
    @display(description="Duration")
    def duration_display(self, obj):
        """Display execution duration."""
        if obj.duration:
            return f"{obj.duration:.3f}s"
        return "-"
    
    @display(description="Arguments Preview")
    def arguments_preview(self, obj):
        """Preview of arguments."""
        if not obj.arguments:
            return "-"
        preview = str(obj.arguments)[:200] + "..." if len(str(obj.arguments)) > 200 else str(obj.arguments)
        return format_html(
            '<div class="text-sm text-gray-600 max-w-md">{}</div>',
            preview
        )
    
    @display(description="Result Preview")
    def result_preview(self, obj):
        """Preview of result."""
        if not obj.result:
            return "-"
        preview = str(obj.result)[:200] + "..." if len(str(obj.result)) > 200 else str(obj.result)
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
    
    @action(description="Retry failed tools", icon="refresh", variant=ActionVariant.WARNING)
    def retry_failed_tools(self, request, queryset):
        """Retry failed tool executions."""
        failed_count = queryset.filter(status='failed').count()
        messages.warning(request, f"Retry functionality not implemented yet. {failed_count} failed tools selected.")
    
    @action(description="Clear errors", icon="clear", variant=ActionVariant.INFO)
    def clear_errors(self, request, queryset):
        """Clear error messages."""
        error_count = queryset.exclude(error_message__isnull=True).exclude(error_message='').count()
        messages.info(request, f"Error clearing not implemented yet. {error_count} tools with errors selected.")
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('user', 'agent_execution')


@admin.register(ApprovalLog)
class ApprovalLogAdmin(ModelAdmin, ExportMixin):
    """Admin interface for ApprovalLog with Unfold styling."""
    
    # Export-only configuration
    export_form_class = ExportForm
    
    list_display = [
        'approval_id_display', 'tool_name_display', 'status_badge', 'user',
        'decision_info', 'time_metrics', 'expiry_status', 'requested_at'
    ]
    ordering = ['-requested_at']
    list_filter = [
        'status', 'tool_name', 'requested_at',
        ('user', AutocompleteSelectFilter),
        ('approved_by', AutocompleteSelectFilter),
        ('rejected_by', AutocompleteSelectFilter)
    ]
    search_fields = ['approval_id', 'tool_name', 'user__username', 'justification']
    autocomplete_fields = ['user', 'approved_by', 'rejected_by']
    readonly_fields = [
        'approval_id', 'requested_at', 'decided_at', 'time_to_decision',
        'is_expired', 'tool_args_preview', 'justification_preview'
    ]
    
    # Unfold form field overrides
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
        JSONField: {"widget": JSONEditorWidget},
    }
    
    fieldsets = (
        ("✅ Approval Info", {
            'fields': ('approval_id', 'tool_name', 'status', 'user'),
            'classes': ('tab',)
        }),
        ("📝 Request Details", {
            'fields': ('tool_args_preview', 'tool_args', 'justification_preview', 'justification'),
            'classes': ('tab',)
        }),
        ("🎯 Decision", {
            'fields': ('approved_by', 'rejected_by', 'rejection_reason'),
            'classes': ('tab',)
        }),
        ("⏰ Timestamps", {
            'fields': ('requested_at', 'decided_at', 'expires_at', 'time_to_decision', 'is_expired'),
            'classes': ('tab', 'collapse')
        }),
    )
    
    actions = ['approve_selected', 'reject_selected', 'extend_expiry']
    
    @display(description="Approval ID")
    def approval_id_display(self, obj):
        """Enhanced approval ID display."""
        return format_html(
            '<span class="font-mono text-sm text-blue-600">#{}</span>',
            obj.approval_id[:8] if obj.approval_id else "N/A"
        )
    
    @display(description="Tool")
    def tool_name_display(self, obj):
        """Enhanced tool name display."""
        return format_html(
            '<div class="flex items-center space-x-2">'
            '<span class="text-purple-600 font-medium">{}</span>'
            '</div>',
            obj.tool_name
        )
    
    @display(description="Status")
    def status_badge(self, obj):
        """Status badge with color coding."""
        colors = {
            'pending': 'bg-yellow-100 text-yellow-800',
            'approved': 'bg-green-100 text-green-800',
            'rejected': 'bg-red-100 text-red-800',
            'expired': 'bg-gray-100 text-gray-800'
        }
        color_class = colors.get(obj.status, 'bg-gray-100 text-gray-800')
        return format_html(
            '<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium {}">{}</span>',
            color_class, obj.get_status_display()
        )
    
    @display(description="Decision")
    def decision_info(self, obj):
        """Decision information."""
        if obj.approved_by:
            return format_html(
                '<div class="text-sm">'
                '<div class="text-green-600 font-medium">✓ Approved by</div>'
                '<div class="text-gray-600">{}</div>'
                '</div>',
                obj.approved_by.username
            )
        elif obj.rejected_by:
            return format_html(
                '<div class="text-sm">'
                '<div class="text-red-600 font-medium">✗ Rejected by</div>'
                '<div class="text-gray-600">{}</div>'
                '</div>',
                obj.rejected_by.username
            )
        return format_html(
            '<div class="text-sm text-yellow-600">⏳ Pending</div>'
        )
    
    @display(description="Time Metrics")
    def time_metrics(self, obj):
        """Time-related metrics."""
        decision_time = f"{obj.time_to_decision:.1f}s" if obj.time_to_decision else "N/A"
        return format_html(
            '<div class="text-sm space-y-1">'
            '<div><span class="font-medium">Decision:</span> {}</div>'
            '</div>',
            decision_time
        )
    
    @display(description="Expiry", boolean=True)
    def expiry_status(self, obj):
        """Expiry status."""
        return not obj.is_expired
    
    @display(description="Tool Args Preview")
    def tool_args_preview(self, obj):
        """Preview of tool arguments."""
        if not obj.tool_args:
            return "-"
        preview = str(obj.tool_args)[:200] + "..." if len(str(obj.tool_args)) > 200 else str(obj.tool_args)
        return format_html(
            '<div class="text-sm text-gray-600 max-w-md">{}</div>',
            preview
        )
    
    @display(description="Justification Preview")
    def justification_preview(self, obj):
        """Preview of justification."""
        if not obj.justification:
            return "-"
        preview = obj.justification[:200] + "..." if len(obj.justification) > 200 else obj.justification
        return format_html(
            '<div class="text-sm text-gray-600 max-w-md">{}</div>',
            preview
        )
    
    @action(description="Approve selected requests", icon="check", variant=ActionVariant.SUCCESS)
    def approve_selected(self, request, queryset):
        """Approve selected requests."""
        count = 0
        for approval in queryset.filter(status='pending'):
            approval.approve(request.user)
            count += 1
        
        messages.success(request, f"Approved {count} requests.")
    
    @action(description="Reject selected requests", icon="close", variant=ActionVariant.DANGER)
    def reject_selected(self, request, queryset):
        """Reject selected requests."""
        count = 0
        for approval in queryset.filter(status='pending'):
            approval.reject(request.user, "Bulk rejection by admin")
            count += 1
        
        messages.warning(request, f"Rejected {count} requests.")
    
    @action(description="Extend expiry", icon="schedule", variant=ActionVariant.INFO)
    def extend_expiry(self, request, queryset):
        """Extend expiry time for selected requests."""
        pending_count = queryset.filter(status='pending').count()
        messages.info(request, f"Expiry extension not implemented yet. {pending_count} pending requests selected.")
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('user', 'approved_by', 'rejected_by')


@admin.register(ToolsetConfiguration)
class ToolsetConfigurationAdmin(ModelAdmin, ImportExportModelAdmin):
    """Admin interface for ToolsetConfiguration with Unfold styling."""
    
    # Import/Export configuration
    import_form_class = ImportForm
    export_form_class = ExportForm
    
    list_display = [
        'name_display', 'toolset_class_badge', 'status_badge', 'usage_info', 'created_by', 'created_at'
    ]
    ordering = ['-created_at']
    list_filter = [
        'is_active', 'created_at',
        ('created_by', AutocompleteSelectFilter)
    ]
    search_fields = ['name', 'description', 'toolset_class']
    autocomplete_fields = ['created_by', 'allowed_users', 'allowed_groups']
    readonly_fields = ['created_at', 'updated_at', 'config_preview']
    
    # Unfold form field overrides
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
        JSONField: {"widget": JSONEditorWidget},
    }
    
    fieldsets = (
        ("🔧 Basic Information", {
            'fields': ('name', 'description', 'toolset_class'),
            'classes': ('tab',)
        }),
        ("⚙️ Configuration", {
            'fields': ('config_preview', 'config'),
            'classes': ('tab',)
        }),
        ("🔐 Access Control", {
            'fields': ('is_active', 'allowed_users', 'allowed_groups'),
            'classes': ('tab',)
        }),
        ("📝 Metadata", {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('tab', 'collapse')
        }),
    )
    
    actions = ['activate_toolsets', 'deactivate_toolsets']
    
    @display(description="Toolset Name")
    def name_display(self, obj):
        """Enhanced name display."""
        return format_html(
            '<div class="flex items-center space-x-2">'
            '<span class="text-teal-600 font-medium">{}</span>'
            '</div>',
            obj.name
        )
    
    @display(description="Class")
    def toolset_class_badge(self, obj):
        """Toolset class badge."""
        if not obj.toolset_class:
            return "-"
        class_name = obj.toolset_class.split('.')[-1] if '.' in obj.toolset_class else obj.toolset_class
        return format_html(
            '<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-cyan-100 text-cyan-800">{}</span>',
            class_name
        )
    
    @display(description="Status", boolean=True)
    def status_badge(self, obj):
        """Status badge."""
        return obj.is_active
    
    @display(description="Usage")
    def usage_info(self, obj):
        """Usage information."""
        users_count = obj.allowed_users.count() if obj.allowed_users.exists() else 0
        groups_count = obj.allowed_groups.count() if obj.allowed_groups.exists() else 0
        
        return format_html(
            '<div class="text-sm space-y-1">'
            '<div><span class="font-medium">Users:</span> {}</div>'
            '<div><span class="font-medium">Groups:</span> {}</div>'
            '</div>',
            users_count,
            groups_count
        )
    
    @display(description="Config Preview")
    def config_preview(self, obj):
        """Preview of configuration."""
        if not obj.config:
            return "-"
        preview = str(obj.config)[:200] + "..." if len(str(obj.config)) > 200 else str(obj.config)
        return format_html(
            '<div class="text-sm text-gray-600 max-w-md">{}</div>',
            preview
        )
    
    @action(description="Activate toolsets", icon="play_arrow", variant=ActionVariant.SUCCESS)
    def activate_toolsets(self, request, queryset):
        """Activate selected toolsets."""
        updated = queryset.update(is_active=True)
        messages.success(request, f"Activated {updated} toolsets.")
    
    @action(description="Deactivate toolsets", icon="pause", variant=ActionVariant.WARNING)
    def deactivate_toolsets(self, request, queryset):
        """Deactivate selected toolsets."""
        updated = queryset.update(is_active=False)
        messages.warning(request, f"Deactivated {updated} toolsets.")
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('created_by').prefetch_related('allowed_users', 'allowed_groups')
