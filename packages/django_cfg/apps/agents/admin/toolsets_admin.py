"""
Toolsets admin interfaces using Django Admin Utilities.

Enhanced toolset management with Material Icons and optimized queries.
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

from ..models.toolsets import ToolExecution, ApprovalLog, ToolsetConfiguration


@admin.register(ToolExecution)
class ToolExecutionAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin, ExportMixin):
    """Enhanced admin for ToolExecution model using Django Admin Utilities."""
    
    # Performance optimization
    select_related_fields = ['agent_execution', 'approval_log']
    
    # Export-only configuration
    export_form_class = ExportForm
    
    list_display = [
        'id_display', 'tool_name_display', 'toolset_display', 'status_display',
        'duration_display', 'retry_count_display', 'created_at_display'
    ]
    list_display_links = ['id_display', 'tool_name_display']
    list_filter = [
        'status', 'tool_name', 'created_at',
        ('agent_execution', AutocompleteSelectFilter)
    ]
    search_fields = ['tool_name', 'toolset_name', 'arguments', 'result']
    autocomplete_fields = ['agent_execution']
    readonly_fields = [
        'id', 'execution_time', 'retry_count', 'created_at', 'started_at', 'completed_at'
    ]
    ordering = ['-created_at']
    
    # Unfold form field overrides
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
        JSONField: {"widget": JSONEditorWidget},
    }
    
    fieldsets = (
        ("🔧 Tool Info", {
            'fields': ('id', 'tool_name', 'toolset_class', 'agent_execution'),
            'classes': ('tab',)
        }),
        ("📝 Execution Data", {
            'fields': ('arguments', 'result', 'error_message'),
            'classes': ('tab',)
        }),
        ("📊 Metrics", {
            'fields': ('execution_time', 'retry_count', 'status'),
            'classes': ('tab',)
        }),
        ("🔐 Approval", {
            'fields': ('approval_log',),
            'classes': ('tab', 'collapse')
        }),
        ("⏰ Timestamps", {
            'fields': ('created_at', 'started_at', 'completed_at'),
            'classes': ('tab', 'collapse')
        }),
    )
    
    actions = ['retry_failed_executions', 'clear_errors']
    
    @display(description="ID")
    def id_display(self, obj):
        """Enhanced ID display."""
        config = StatusBadgeConfig(show_icons=True, icon=Icons.TAG)
        return StatusBadge.create(
            text=f"#{str(obj.id)[:8]}",
            variant="secondary",
            config=config
        )
    
    @display(description="Tool")
    def tool_name_display(self, obj):
        """Enhanced tool name display."""
        config = StatusBadgeConfig(show_icons=True, icon=Icons.BUILD)
        return StatusBadge.create(
            text=obj.tool_name,
            variant="primary",
            config=config
        )
    
    @display(description="Toolset")
    def toolset_display(self, obj):
        """Toolset class display with badge."""
        if not obj.toolset_class:
            return "—"
        
        # Extract class name from full path
        class_name = obj.toolset_class.split('.')[-1] if '.' in obj.toolset_class else obj.toolset_class
        
        config = StatusBadgeConfig(show_icons=True, icon=Icons.EXTENSION)
        return StatusBadge.create(
            text=class_name,
            variant="info",
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
    
    @display(description="Duration")
    def duration_display(self, obj):
        """Execution duration display."""
        if obj.execution_time:
            return f"{obj.execution_time:.3f}s"
        return "—"
    
    @display(description="Retries")
    def retry_count_display(self, obj):
        """Retry count display with badge."""
        if obj.retry_count > 0:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.REFRESH)
            variant = "warning" if obj.retry_count > 2 else "info"
            return StatusBadge.create(
                text=str(obj.retry_count),
                variant=variant,
                config=config
            )
        return "0"
    
    @display(description="Created")
    def created_at_display(self, obj):
        """Created time with relative display."""
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'created_at', config)
    
    @action(description="Retry failed executions", variant=ActionVariant.WARNING)
    def retry_failed_executions(self, request, queryset):
        """Retry failed tool executions."""
        failed_count = queryset.filter(status='failed').count()
        messages.warning(request, f"Retry functionality not implemented yet. {failed_count} failed executions selected.")
    
    @action(description="Clear error messages", variant=ActionVariant.INFO)
    def clear_errors(self, request, queryset):
        """Clear error messages from executions."""
        updated = queryset.update(error_message=None)
        messages.info(request, f"Cleared error messages from {updated} executions.")


@admin.register(ApprovalLog)
class ApprovalLogAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin, ExportMixin):
    """Enhanced admin for ApprovalLog model using Django Admin Utilities."""
    
    # Performance optimization
    select_related_fields = ['approved_by']
    
    # Export-only configuration
    export_form_class = ExportForm
    
    list_display = [
        'approval_id_display', 'tool_name_display', 'status_display',
        'approved_by_display', 'decision_time_display', 'expires_at_display'
    ]
    list_display_links = ['approval_id_display', 'tool_name_display']
    list_filter = [
        'status', 'tool_name', 'requested_at', 'expires_at',
        ('approved_by', AutocompleteSelectFilter)
    ]
    search_fields = ['tool_name', 'tool_args', 'justification']
    autocomplete_fields = ['approved_by']
    readonly_fields = [
        'id', 'requested_at', 'decided_at', 'expires_at'
    ]
    ordering = ['-requested_at']
    
    # Unfold form field overrides
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
        JSONField: {"widget": JSONEditorWidget},
    }
    
    fieldsets = (
        ("🔐 Approval Info", {
            'fields': ('id', 'tool_name', 'status', 'approved_by'),
            'classes': ('tab',)
        }),
        ("📝 Request Details", {
            'fields': ('tool_arguments', 'justification'),
            'classes': ('tab',)
        }),
        ("⏰ Timing", {
            'fields': ('created_at', 'decision_time', 'expires_at'),
            'classes': ('tab',)
        }),
    )
    
    actions = ['approve_pending', 'reject_pending', 'extend_expiry']
    
    @display(description="Approval ID")
    def approval_id_display(self, obj):
        """Enhanced approval ID display."""
        config = StatusBadgeConfig(show_icons=True, icon=Icons.VERIFIED)
        return StatusBadge.create(
            text=f"#{str(obj.id)[:8]}",
            variant="secondary",
            config=config
        )
    
    @display(description="Tool")
    def tool_name_display(self, obj):
        """Enhanced tool name display."""
        config = StatusBadgeConfig(show_icons=True, icon=Icons.BUILD)
        return StatusBadge.create(
            text=obj.tool_name,
            variant="primary",
            config=config
        )
    
    @display(description="Status")
    def status_display(self, obj):
        """Status display with appropriate icons."""
        status_config = StatusBadgeConfig(
            custom_mappings={
                'pending': 'warning',
                'approved': 'success',
                'rejected': 'danger',
                'expired': 'secondary'
            },
            show_icons=True,
            icon=Icons.CHECK_CIRCLE if obj.status == 'approved' else Icons.CANCEL if obj.status == 'rejected' else Icons.SCHEDULE if obj.status == 'pending' else Icons.TIMER_OFF
        )
        return self.display_status_auto(obj, 'status', status_config)
    
    @display(description="Approved By")
    def approved_by_display(self, obj):
        """Approved by user display."""
        if not obj.approved_by:
            return "—"
        return self.display_user_simple(obj.approved_by)
    
    @display(description="Decision Time")
    def decision_time_display(self, obj):
        """Decision time display."""
        if obj.decision_time:
            return f"{obj.decision_time:.2f}s"
        return "—"
    
    @display(description="Expires")
    def expires_at_display(self, obj):
        """Expiry time with relative display."""
        if not obj.expires_at:
            return "—"
        
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'expires_at', config)
    
    @action(description="Approve pending", variant=ActionVariant.SUCCESS)
    def approve_pending(self, request, queryset):
        """Approve pending approvals."""
        updated = queryset.filter(status='pending').update(
            status='approved',
            approved_by=request.user,
            decision_time=timezone.now()
        )
        messages.success(request, f"Approved {updated} pending requests.")
    
    @action(description="Reject pending", variant=ActionVariant.DANGER)
    def reject_pending(self, request, queryset):
        """Reject pending approvals."""
        updated = queryset.filter(status='pending').update(
            status='rejected',
            approved_by=request.user,
            decision_time=timezone.now()
        )
        messages.warning(request, f"Rejected {updated} pending requests.")
    
    @action(description="Extend expiry", variant=ActionVariant.INFO)
    def extend_expiry(self, request, queryset):
        """Extend expiry time for pending approvals."""
        from datetime import timedelta
        new_expiry = timezone.now() + timedelta(hours=24)
        updated = queryset.filter(status='pending').update(expires_at=new_expiry)
        messages.info(request, f"Extended expiry for {updated} approvals by 24 hours.")


@admin.register(ToolsetConfiguration)
class ToolsetConfigurationAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin, ExportMixin):
    """Enhanced admin for ToolsetConfiguration model using Django Admin Utilities."""
    
    # Performance optimization
    select_related_fields = ['created_by']
    
    # Export-only configuration
    export_form_class = ExportForm
    
    list_display = [
        'name_display', 'toolset_class_display', 'status_display',
        'usage_count_display', 'created_by_display', 'created_at_display'
    ]
    list_display_links = ['name_display']
    list_filter = [
        'is_active', 'toolset_class', 'created_at',
        ('created_by', AutocompleteSelectFilter)
    ]
    search_fields = ['name', 'description', 'toolset_class']
    autocomplete_fields = ['created_by']
    readonly_fields = [
        'id', 'created_at', 'updated_at'
    ]
    ordering = ['-created_at']
    
    # Unfold form field overrides
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
        JSONField: {"widget": JSONEditorWidget},
    }
    
    fieldsets = (
        ("⚙️ Configuration Info", {
            'fields': ('id', 'name', 'description', 'toolset_class'),
            'classes': ('tab',)
        }),
        ("🔧 Settings", {
            'fields': ('configuration', 'is_active'),
            'classes': ('tab',)
        }),
        ("📊 Usage", {
            'fields': ('usage_count',),
            'classes': ('tab',)
        }),
        ("👤 Metadata", {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('tab', 'collapse')
        }),
    )
    
    actions = ['activate_configurations', 'deactivate_configurations', 'reset_usage']
    
    @display(description="Configuration Name")
    def name_display(self, obj):
        """Enhanced configuration name display."""
        config = StatusBadgeConfig(show_icons=True, icon=Icons.SETTINGS)
        return StatusBadge.create(
            text=obj.name,
            variant="primary",
            config=config
        )
    
    @display(description="Toolset Class")
    def toolset_class_display(self, obj):
        """Toolset class display with badge."""
        if not obj.toolset_class:
            return "—"
        
        # Extract class name from full path
        class_name = obj.toolset_class.split('.')[-1] if '.' in obj.toolset_class else obj.toolset_class
        
        config = StatusBadgeConfig(show_icons=True, icon=Icons.EXTENSION)
        return StatusBadge.create(
            text=class_name,
            variant="info",
            config=config
        )
    
    @display(description="Status")
    def status_display(self, obj):
        """Status display based on active state."""
        if obj.is_active:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.CHECK_CIRCLE)
            return StatusBadge.create(text="Active", variant="success", config=config)
        else:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.PAUSE_CIRCLE)
            return StatusBadge.create(text="Inactive", variant="secondary", config=config)
    
    @display(description="Usage")
    def usage_count_display(self, obj):
        """Usage count display."""
        if not obj.usage_count:
            return "Not used"
        return f"{obj.usage_count} times"
    
    @display(description="Created By")
    def created_by_display(self, obj):
        """Created by user display."""
        if not obj.created_by:
            return "—"
        return self.display_user_simple(obj.created_by)
    
    @display(description="Created")
    def created_at_display(self, obj):
        """Created time with relative display."""
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'created_at', config)
    
    @action(description="Activate configurations", variant=ActionVariant.SUCCESS)
    def activate_configurations(self, request, queryset):
        """Activate selected configurations."""
        updated = queryset.update(is_active=True)
        messages.success(request, f"Activated {updated} configurations.")
    
    @action(description="Deactivate configurations", variant=ActionVariant.WARNING)
    def deactivate_configurations(self, request, queryset):
        """Deactivate selected configurations."""
        updated = queryset.update(is_active=False)
        messages.warning(request, f"Deactivated {updated} configurations.")
    
    @action(description="Reset usage count", variant=ActionVariant.INFO)
    def reset_usage(self, request, queryset):
        """Reset usage count for selected configurations."""
        updated = queryset.update(usage_count=0)
        messages.info(request, f"Reset usage count for {updated} configurations.")