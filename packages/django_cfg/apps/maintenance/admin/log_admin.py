"""
MaintenanceLog admin using Django Admin Utilities.

Read-only admin interface for viewing maintenance operation logs.
"""

from django.contrib import admin
from django.http import HttpRequest
from django.db import models
from django.db.models import Count, Q
from typing import Any
import json
from unfold.admin import ModelAdmin

from django_cfg.modules.django_admin import (
    OptimizedModelAdmin,
    DisplayMixin,
    StatusBadgeConfig,
    DateTimeDisplayConfig,
    Icons,
    display
)
from django_cfg.modules.django_admin.utils.badges import StatusBadge

from ..models import MaintenanceLog


@admin.register(MaintenanceLog)
class MaintenanceLogAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin):
    """Admin interface for MaintenanceLog model using Django Admin Utilities."""
    
    # Performance optimization
    select_related_fields = ['site']
    
    list_display = [
        'status_display',
        'site_display',
        'action_display',
        'created_at_display',
        'duration_display',
        'error_preview'
    ]
    list_display_links = ['site_display']
    ordering = ['-created_at']
    list_filter = [
        'action',
        'status',
        'created_at',
        'site'
    ]
    search_fields = [
        'site__name',
        'site__domain',
        'reason',
        'error_message'
    ]
    readonly_fields = [
        'site',
        'action',
        'status',
        'reason',
        'error_message',
        'cloudflare_response',
        'created_at',
        'duration_seconds',
        'cloudflare_response_formatted'
    ]
    
    fieldsets = [
        ('📋 Log Information', {
            'fields': ['site', 'action', 'status', 'reason'],
            'classes': ('tab',)
        }),
        ('⏱️ Timing', {
            'fields': ['created_at', 'duration_seconds'],
            'classes': ('tab',)
        }),
        ('❌ Error Details', {
            'fields': ['error_message'],
            'classes': ('tab', 'collapse')
        }),
        ('📊 Cloudflare Response', {
            'fields': ['cloudflare_response_formatted'],
            'classes': ('tab', 'collapse')
        })
    ]
    
    def has_add_permission(self, request):
        """Disable adding new logs through admin."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing logs through admin."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Allow deleting old logs."""
        return True
    
    @display(description="Status")
    def status_display(self, obj: MaintenanceLog) -> str:
        """Display status with badge."""
        status_variants = {
            MaintenanceLog.Status.SUCCESS: 'success',
            MaintenanceLog.Status.FAILED: 'danger',
            MaintenanceLog.Status.PENDING: 'warning'
        }
        variant = status_variants.get(obj.status, 'secondary')
        
        status_icons = {
            MaintenanceLog.Status.SUCCESS: Icons.CHECK_CIRCLE,
            MaintenanceLog.Status.FAILED: Icons.CANCEL,
            MaintenanceLog.Status.PENDING: Icons.SCHEDULE
        }
        icon = status_icons.get(obj.status, Icons.HELP)
        
        config = StatusBadgeConfig(show_icons=True, icon=icon)
        return StatusBadge.create(
            text=obj.get_status_display(),
            variant=variant,
            config=config
        )
    
    @display(description="Site", ordering="site__name")
    def site_display(self, obj: MaintenanceLog) -> str:
        """Display site name."""
        if not obj.site:
            return "—"
        
        config = StatusBadgeConfig(show_icons=True, icon=Icons.LANGUAGE)
        return StatusBadge.create(
            text=f"{obj.site.name} ({obj.site.domain})",
            variant="info",
            config=config
        )
    
    @display(description="Action")
    def action_display(self, obj: MaintenanceLog) -> str:
        """Display action with badge."""
        action_variants = {
            MaintenanceLog.Action.ENABLE: 'warning',
            MaintenanceLog.Action.DISABLE: 'success',
            MaintenanceLog.Action.CHECK_STATUS: 'info'
        }
        variant = action_variants.get(obj.action, 'secondary')
        
        action_icons = {
            MaintenanceLog.Action.ENABLE: Icons.BUILD,
            MaintenanceLog.Action.DISABLE: Icons.CHECK_CIRCLE,
            MaintenanceLog.Action.CHECK_STATUS: Icons.VISIBILITY
        }
        icon = action_icons.get(obj.action, Icons.SETTINGS)
        
        config = StatusBadgeConfig(show_icons=True, icon=icon)
        return StatusBadge.create(
            text=obj.get_action_display(),
            variant=variant,
            config=config
        )
    
    @display(description="Created")
    def created_at_display(self, obj: MaintenanceLog) -> str:
        """Created time with relative display."""
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'created_at', config)
    
    @display(description="Duration")
    def duration_display(self, obj: MaintenanceLog) -> str:
        """Display operation duration."""
        if obj.duration_seconds is None:
            return "—"
        
        if obj.duration_seconds < 1:
            return f"{obj.duration_seconds * 1000:.0f}ms"
        elif obj.duration_seconds < 60:
            return f"{obj.duration_seconds:.1f}s"
        else:
            minutes = obj.duration_seconds // 60
            seconds = obj.duration_seconds % 60
            return f"{minutes:.0f}m {seconds:.0f}s"
    
    @display(description="Error")
    def error_preview(self, obj: MaintenanceLog) -> str:
        """Show error message preview."""
        if not obj.error_message:
            return "—"
        
        preview = obj.error_message[:100]
        if len(obj.error_message) > 100:
            preview += "..."
        
        return preview
    
    def cloudflare_response_formatted(self, obj: MaintenanceLog) -> str:
        """Format cloudflare response for display."""
        if not obj.cloudflare_response:
            return "No response data"
        
        try:
            if isinstance(obj.cloudflare_response, str):
                data = json.loads(obj.cloudflare_response)
            else:
                data = obj.cloudflare_response
            
            return json.dumps(data, indent=2, ensure_ascii=False)
        except (json.JSONDecodeError, TypeError):
            return str(obj.cloudflare_response)
    
    cloudflare_response_formatted.short_description = "Cloudflare Response (Formatted)"
    
    def changelist_view(self, request, extra_context=None):
        """Add log statistics to changelist."""
        extra_context = extra_context or {}
        
        queryset = self.get_queryset(request)
        stats = queryset.aggregate(
            total_logs=Count('id'),
            success_logs=Count('id', filter=Q(status=MaintenanceLog.Status.SUCCESS)),
            failed_logs=Count('id', filter=Q(status=MaintenanceLog.Status.FAILED)),
            pending_logs=Count('id', filter=Q(status=MaintenanceLog.Status.PENDING))
        )
        
        # Action breakdown
        action_counts = dict(
            queryset.values_list('action').annotate(
                count=Count('id')
            )
        )
        
        extra_context['log_stats'] = {
            'total_logs': stats['total_logs'] or 0,
            'success_logs': stats['success_logs'] or 0,
            'failed_logs': stats['failed_logs'] or 0,
            'pending_logs': stats['pending_logs'] or 0,
            'action_counts': action_counts
        }
        
        return super().changelist_view(request, extra_context)
