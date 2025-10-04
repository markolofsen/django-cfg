"""
ScheduledMaintenance admin using Django Admin Utilities.

Enhanced scheduled maintenance management with Material Icons and optimized queries.
"""

from django.contrib import admin, messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.urls import path, reverse
from django.template.response import TemplateResponse
from django.db import models
from django.db.models import Count, Q
from typing import Any
from unfold.admin import ModelAdmin

from django_cfg.modules.django_admin import (
    OptimizedModelAdmin,
    DisplayMixin,
    StatusBadgeConfig,
    DateTimeDisplayConfig,
    Icons,
    ActionVariant,
    display,
    action
)
from django_cfg.modules.django_admin.utils.badges import StatusBadge

from ..models import ScheduledMaintenance, CloudflareSite


@admin.register(ScheduledMaintenance)
class ScheduledMaintenanceAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin):
    """Admin for ScheduledMaintenance using Django Admin Utilities."""
    
    list_display = [
        "status_display",
        "title_display",
        "scheduled_start_display",
        "duration_display",
        "sites_count",
        "priority_display",
        "auto_flags_display",
        "created_at_display",
    ]
    list_display_links = ["title_display"]
    ordering = ["-scheduled_start"]
    search_fields = ["title", "description", "maintenance_message"]
    list_filter = [
        "status", 
        "priority", 
        "auto_enable", 
        "auto_disable",
        "scheduled_start",
        "created_at"
    ]
    
    fieldsets = [
        ("📋 Basic Information", {
            "fields": ["title", "description"],
            "classes": ("tab",)
        }),
        ("⏰ Scheduling", {
            "fields": ["scheduled_start", "duration_minutes"],
            "classes": ("tab",)
        }),
        ("🌐 Sites", {
            "fields": ["sites"],
            "classes": ("tab",)
        }),
        ("⚙️ Settings", {
            "fields": ["priority", "auto_enable", "auto_disable"],
            "classes": ("tab",)
        }),
        ("💬 Messages", {
            "fields": ["maintenance_message"],
            "classes": ("tab", "collapse")
        }),
        ("📊 Status", {
            "fields": ["status"],
            "classes": ("tab",)
        }),
        ("⏰ Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ("tab", "collapse")
        }),
    ]
    
    filter_horizontal = ["sites"]
    
    actions = [
        "execute_maintenance_action",
        "cancel_maintenance_action",
        "reschedule_maintenance_action"
    ]
    
    @display(description="Status")
    def status_display(self, obj: ScheduledMaintenance) -> str:
        """Display status with badge."""
        status_variants = {
            ScheduledMaintenance.Status.SCHEDULED: 'warning',
            ScheduledMaintenance.Status.ACTIVE: 'info',
            ScheduledMaintenance.Status.COMPLETED: 'success',
            ScheduledMaintenance.Status.CANCELLED: 'secondary',
            ScheduledMaintenance.Status.FAILED: 'danger'
        }
        variant = status_variants.get(obj.status, 'secondary')
        
        status_icons = {
            ScheduledMaintenance.Status.SCHEDULED: Icons.SCHEDULE,
            ScheduledMaintenance.Status.ACTIVE: Icons.PLAY_ARROW,
            ScheduledMaintenance.Status.COMPLETED: Icons.CHECK_CIRCLE,
            ScheduledMaintenance.Status.CANCELLED: Icons.CANCEL,
            ScheduledMaintenance.Status.FAILED: Icons.ERROR
        }
        icon = status_icons.get(obj.status, Icons.HELP)
        
        config = StatusBadgeConfig(show_icons=True, icon=icon)
        return StatusBadge.create(
            text=obj.get_status_display(),
            variant=variant,
            config=config
        )
    
    @display(description="Title", ordering="title")
    def title_display(self, obj: ScheduledMaintenance) -> str:
        """Display maintenance title."""
        config = StatusBadgeConfig(show_icons=True, icon=Icons.EVENT)
        return StatusBadge.create(
            text=obj.title,
            variant="primary",
            config=config
        )
    
    @display(description="Scheduled Start")
    def scheduled_start_display(self, obj: ScheduledMaintenance) -> str:
        """Display scheduled start time."""
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'scheduled_start', config)
    
    @display(description="Duration")
    def duration_display(self, obj: ScheduledMaintenance) -> str:
        """Display maintenance duration."""
        if obj.duration_minutes < 60:
            return f"{obj.duration_minutes} min"
        else:
            hours = obj.duration_minutes // 60
            minutes = obj.duration_minutes % 60
            if minutes == 0:
                return f"{hours}h"
            else:
                return f"{hours}h {minutes}m"
    
    @display(description="Sites")
    def sites_count(self, obj: ScheduledMaintenance) -> str:
        """Display count of affected sites."""
        count = obj.sites.count()
        if count == 0:
            return "No sites"
        elif count == 1:
            return "1 site"
        else:
            return f"{count} sites"
    
    @display(description="Priority")
    def priority_display(self, obj: ScheduledMaintenance) -> str:
        """Display priority with badge."""
        priority_variants = {
            ScheduledMaintenance.Priority.LOW: 'secondary',
            ScheduledMaintenance.Priority.MEDIUM: 'info',
            ScheduledMaintenance.Priority.HIGH: 'warning',
            ScheduledMaintenance.Priority.CRITICAL: 'danger'
        }
        variant = priority_variants.get(obj.priority, 'secondary')
        
        priority_icons = {
            ScheduledMaintenance.Priority.LOW: Icons.KEYBOARD_ARROW_DOWN,
            ScheduledMaintenance.Priority.MEDIUM: Icons.REMOVE,
            ScheduledMaintenance.Priority.HIGH: Icons.KEYBOARD_ARROW_UP,
            ScheduledMaintenance.Priority.CRITICAL: Icons.PRIORITY_HIGH
        }
        icon = priority_icons.get(obj.priority, Icons.HELP)
        
        config = StatusBadgeConfig(show_icons=True, icon=icon)
        return StatusBadge.create(
            text=obj.get_priority_display(),
            variant=variant,
            config=config
        )
    
    @display(description="Auto Flags")
    def auto_flags_display(self, obj: ScheduledMaintenance) -> str:
        """Display auto enable/disable flags."""
        flags = []
        if obj.auto_enable:
            flags.append("Auto Enable")
        if obj.auto_disable:
            flags.append("Auto Disable")
        
        if not flags:
            return "Manual"
        
        return " | ".join(flags)
    
    @display(description="Created")
    def created_at_display(self, obj: ScheduledMaintenance) -> str:
        """Created time with relative display."""
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'created_at', config)
    
    @action(description="Execute maintenance", variant=ActionVariant.WARNING)
    def execute_maintenance_action(self, request: HttpRequest, queryset) -> None:
        """Execute selected maintenance tasks."""
        scheduled_count = queryset.filter(status=ScheduledMaintenance.Status.SCHEDULED).count()
        if scheduled_count == 0:
            messages.error(request, "No scheduled maintenance tasks selected.")
            return
        
        # Update status to active
        queryset.filter(status=ScheduledMaintenance.Status.SCHEDULED).update(
            status=ScheduledMaintenance.Status.ACTIVE
        )
        
        messages.success(request, f"Started execution of {scheduled_count} maintenance tasks.")
    
    @action(description="Cancel maintenance", variant=ActionVariant.DANGER)
    def cancel_maintenance_action(self, request: HttpRequest, queryset) -> None:
        """Cancel selected maintenance tasks."""
        cancelable_count = queryset.filter(
            status__in=[ScheduledMaintenance.Status.SCHEDULED, ScheduledMaintenance.Status.ACTIVE]
        ).count()
        
        if cancelable_count == 0:
            messages.error(request, "No cancelable maintenance tasks selected.")
            return
        
        queryset.filter(
            status__in=[ScheduledMaintenance.Status.SCHEDULED, ScheduledMaintenance.Status.ACTIVE]
        ).update(status=ScheduledMaintenance.Status.CANCELLED)
        
        messages.warning(request, f"Cancelled {cancelable_count} maintenance tasks.")
    
    @action(description="Reschedule maintenance", variant=ActionVariant.INFO)
    def reschedule_maintenance_action(self, request: HttpRequest, queryset) -> None:
        """Reschedule selected maintenance tasks."""
        reschedulable_count = queryset.filter(
            status__in=[ScheduledMaintenance.Status.CANCELLED, ScheduledMaintenance.Status.FAILED]
        ).count()
        
        if reschedulable_count == 0:
            messages.error(request, "No reschedulable maintenance tasks selected.")
            return
        
        # Reset to scheduled status
        queryset.filter(
            status__in=[ScheduledMaintenance.Status.CANCELLED, ScheduledMaintenance.Status.FAILED]
        ).update(status=ScheduledMaintenance.Status.SCHEDULED)
        
        messages.info(request, f"Reset {reschedulable_count} maintenance tasks to scheduled.")
    
    def changelist_view(self, request, extra_context=None):
        """Add maintenance statistics to changelist."""
        extra_context = extra_context or {}
        
        queryset = self.get_queryset(request)
        stats = queryset.aggregate(
            total_maintenance=Count('id'),
            scheduled_maintenance=Count('id', filter=Q(status=ScheduledMaintenance.Status.SCHEDULED)),
            active_maintenance=Count('id', filter=Q(status=ScheduledMaintenance.Status.ACTIVE)),
            completed_maintenance=Count('id', filter=Q(status=ScheduledMaintenance.Status.COMPLETED)),
            failed_maintenance=Count('id', filter=Q(status=ScheduledMaintenance.Status.FAILED)),
            cancelled_maintenance=Count('id', filter=Q(status=ScheduledMaintenance.Status.CANCELLED))
        )
        
        # Priority breakdown
        priority_counts = dict(
            queryset.values_list('priority').annotate(
                count=Count('id')
            )
        )
        
        # Upcoming maintenance (next 7 days)
        upcoming_maintenance = queryset.filter(
            scheduled_start__gte=timezone.now(),
            scheduled_start__lte=timezone.now() + timezone.timedelta(days=7),
            status=ScheduledMaintenance.Status.SCHEDULED
        ).count()
        
        extra_context['maintenance_stats'] = {
            'total_maintenance': stats['total_maintenance'] or 0,
            'scheduled_maintenance': stats['scheduled_maintenance'] or 0,
            'active_maintenance': stats['active_maintenance'] or 0,
            'completed_maintenance': stats['completed_maintenance'] or 0,
            'failed_maintenance': stats['failed_maintenance'] or 0,
            'cancelled_maintenance': stats['cancelled_maintenance'] or 0,
            'priority_counts': priority_counts,
            'upcoming_maintenance': upcoming_maintenance
        }
        
        return super().changelist_view(request, extra_context)
