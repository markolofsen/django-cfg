"""
MaintenanceLog admin with Unfold styling.

Read-only admin interface for viewing maintenance operation logs.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpRequest
from typing import Any
import json

from unfold.admin import ModelAdmin
from unfold.decorators import display

from ..models import MaintenanceLog


@admin.register(MaintenanceLog)
class MaintenanceLogAdmin(ModelAdmin):
    """Admin interface for MaintenanceLog model."""
    
    list_display = [
        'status_display',
        'site',
        'action_display',
        'created_at',
        'duration_display',
        'error_preview'
    ]
    
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
        ('Operation Details', {
            'fields': ['site', 'action', 'status', 'created_at', 'duration_seconds']
        }),
        ('Additional Information', {
            'fields': ['reason', 'error_message']
        }),
        ('Cloudflare Response', {
            'fields': ['cloudflare_response_formatted'],
            'classes': ['collapse']
        })
    ]
    
    ordering = ['-created_at']
    
    def has_add_permission(self, request: HttpRequest) -> bool:
        """Logs are created automatically, no manual adding."""
        return False
    
    def has_change_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        """Logs are read-only."""
        return False
    
    def has_delete_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        """Allow deletion of old logs."""
        return True
    
    # Display methods
    
    @display(description="Status", ordering="status")
    def status_display(self, obj: MaintenanceLog) -> str:
        """Display status with emoji and badge."""
        status_emoji = {
            MaintenanceLog.Status.SUCCESS: "✅",
            MaintenanceLog.Status.FAILED: "❌",
            MaintenanceLog.Status.PENDING: "⏳"
        }.get(obj.status, "❓")
        
        color_class = {
            MaintenanceLog.Status.SUCCESS: "badge-success",
            MaintenanceLog.Status.FAILED: "badge-danger",
            MaintenanceLog.Status.PENDING: "badge-warning"
        }.get(obj.status, "badge-secondary")
        
        return format_html(
            '<span class="badge {}">{} {}</span>',
            color_class, status_emoji, obj.get_status_display()
        )
    
    @display(description="Action", ordering="action")
    def action_display(self, obj: MaintenanceLog) -> str:
        """Display action with icon."""
        action_icons = {
            MaintenanceLog.Action.ENABLE: "🔧",
            MaintenanceLog.Action.DISABLE: "🟢", 
            MaintenanceLog.Action.SYNC: "🔄",
            MaintenanceLog.Action.ERROR: "❌"
        }
        
        icon = action_icons.get(obj.action, "❓")
        return f"{icon} {obj.get_action_display()}"
    
    @display(description="Duration")
    def duration_display(self, obj: MaintenanceLog) -> str:
        """Display operation duration."""
        if not obj.duration_seconds:
            return "-"
        
        if obj.duration_seconds < 60:
            return f"{obj.duration_seconds}s"
        else:
            minutes = obj.duration_seconds // 60
            seconds = obj.duration_seconds % 60
            return f"{minutes}m {seconds}s"
    
    @display(description="Error")
    def error_preview(self, obj: MaintenanceLog) -> str:
        """Show error message preview."""
        if not obj.error_message:
            return "-"
        
        preview = obj.error_message[:100]
        if len(obj.error_message) > 100:
            preview += "..."
        
        return format_html('<span style="color: red; font-family: monospace;">{}</span>', preview)
    
    def cloudflare_response_formatted(self, obj: MaintenanceLog) -> str:
        """Format Cloudflare response for display."""
        if not obj.cloudflare_response:
            return "No response data"
        
        try:
            formatted = json.dumps(obj.cloudflare_response, indent=2)
            return format_html('<pre style="background: #f8f8f8; padding: 10px; overflow: auto;">{}</pre>', formatted)
        except Exception:
            return str(obj.cloudflare_response)
    
    cloudflare_response_formatted.short_description = "Cloudflare Response (Formatted)"
