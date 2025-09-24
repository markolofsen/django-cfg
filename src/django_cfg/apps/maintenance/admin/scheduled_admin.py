"""
Admin interface for ScheduledMaintenance with Unfold styling.

Provides comprehensive management of scheduled maintenance events.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from django.urls import path, reverse
from django.template.response import TemplateResponse
from typing import Any

from unfold.admin import ModelAdmin
from unfold.decorators import display, action
from unfold.enums import ActionVariant

from ..models import ScheduledMaintenance, CloudflareSite


@admin.register(ScheduledMaintenance)
class ScheduledMaintenanceAdmin(ModelAdmin):
    """Admin for ScheduledMaintenance with Unfold styling."""
    
    list_display = [
        "status_display",
        "title",
        "scheduled_start",
        "duration_display",
        "sites_count",
        "priority_badge",
        "auto_flags",
        "created_at",
    ]
    list_display_links = ["title"]
    search_fields = ["title", "description", "maintenance_message"]
    list_filter = [
        "status", 
        "priority", 
        "auto_enable", 
        "auto_disable",
        "scheduled_start",
        "created_at"
    ]
    ordering = ["-scheduled_start"]
    
    fieldsets = [
        ("Basic Information", {
            'fields': ['title', 'description', 'priority', 'created_by']
        }),
        ("Scheduling", {
            'fields': ['scheduled_start', 'estimated_duration', 'scheduled_end']
        }),
        ("Sites", {
            'fields': ['sites']
        }),
        ("Configuration", {
            'fields': ['maintenance_message', 'template', 'auto_enable', 'auto_disable']
        }),
        ("Notifications", {
            'fields': ['notify_before', 'notify_on_start', 'notify_on_complete'],
            'classes': ['collapse']
        }),
        ("Execution Status", {
            'fields': ['status', 'actual_start', 'actual_end'],
            'classes': ['collapse']
        }),
        ("Execution Log", {
            'fields': ['execution_log'],
            'classes': ['collapse']
        }),
    ]
    
    readonly_fields = ['scheduled_end', 'actual_start', 'actual_end', 'execution_log']
    
    filter_horizontal = ['sites']
    
    actions = [
        'start_maintenance_action',
        'complete_maintenance_action', 
        'cancel_maintenance_action',
        'duplicate_maintenance_action'
    ]
    
    def get_urls(self):
        """Add custom admin URLs."""
        urls = super().get_urls()
        custom_urls = [
            path(
                'calendar/',
                self.admin_site.admin_view(self.calendar_view),
                name='scheduled_maintenance_calendar'
            ),
            path(
                '<int:object_id>/start/',
                self.admin_site.admin_view(self.start_maintenance_view),
                name='scheduled_maintenance_start'
            ),
            path(
                '<int:object_id>/complete/',
                self.admin_site.admin_view(self.complete_maintenance_view),
                name='scheduled_maintenance_complete'
            ),
        ]
        return custom_urls + urls
    
    @display(description="Status")
    def status_display(self, obj: ScheduledMaintenance) -> str:
        """Display status with colored badge and timing info."""
        status_config = {
            ScheduledMaintenance.Status.SCHEDULED: {
                'emoji': '📅',
                'color': 'blue',
                'text': 'Scheduled'
            },
            ScheduledMaintenance.Status.ACTIVE: {
                'emoji': '🔧',
                'color': 'orange',
                'text': 'Active'
            },
            ScheduledMaintenance.Status.COMPLETED: {
                'emoji': '✅',
                'color': 'green',
                'text': 'Completed'
            },
            ScheduledMaintenance.Status.CANCELLED: {
                'emoji': '❌',
                'color': 'red',
                'text': 'Cancelled'
            },
            ScheduledMaintenance.Status.FAILED: {
                'emoji': '💥',
                'color': 'red',
                'text': 'Failed'
            },
        }
        
        config = status_config.get(obj.status, {
            'emoji': '❓',
            'color': 'gray',
            'text': obj.get_status_display()
        })
        
        # Add timing info
        timing_info = ""
        if obj.status == ScheduledMaintenance.Status.SCHEDULED:
            if obj.is_due:
                timing_info = " <small>(Due now!)</small>"
            elif obj.time_until_start:
                hours = int(obj.time_until_start.total_seconds() // 3600)
                if hours < 24:
                    timing_info = f" <small>(in {hours}h)</small>"
        elif obj.status == ScheduledMaintenance.Status.ACTIVE:
            if obj.is_overdue:
                timing_info = " <small>(Overdue!)</small>"
            elif obj.time_until_end:
                hours = int(obj.time_until_end.total_seconds() // 3600)
                minutes = int((obj.time_until_end.total_seconds() % 3600) // 60)
                timing_info = f" <small>({hours}h {minutes}m left)</small>"
        
        return format_html(
            '<span style="color: {};">{} {}</span>{}',
            config['color'],
            config['emoji'],
            config['text'],
            timing_info
        )
    
    @display(description="Duration")
    def duration_display(self, obj: ScheduledMaintenance) -> str:
        """Display estimated vs actual duration."""
        estimated_hours = obj.estimated_duration.total_seconds() / 3600
        
        if obj.actual_duration:
            actual_hours = obj.actual_duration.total_seconds() / 3600
            return format_html(
                '{:.1f}h <small>(actual: {:.1f}h)</small>',
                estimated_hours,
                actual_hours
            )
        
        return f"{estimated_hours:.1f}h"
    
    @display(description="Sites")
    def sites_count(self, obj: ScheduledMaintenance) -> str:
        """Display sites count with link."""
        count = obj.affected_sites_count
        if count == 0:
            return format_html('<span style="color: red;">No sites</span>')
        
        return format_html(
            '<span class="badge badge-info">{} sites</span>',
            count
        )
    
    @display(description="Priority")
    def priority_badge(self, obj: ScheduledMaintenance) -> str:
        """Display priority badge."""
        priority_config = {
            'low': {'color': 'green', 'emoji': '🟢'},
            'normal': {'color': 'blue', 'emoji': '🟡'},
            'high': {'color': 'orange', 'emoji': '🟠'},
            'critical': {'color': 'red', 'emoji': '🔴'},
        }
        
        config = priority_config.get(obj.priority, {'color': 'gray', 'emoji': '⚪'})
        
        return format_html(
            '<span style="color: {};">{} {}</span>',
            config['color'],
            config['emoji'],
            obj.get_priority_display()
        )
    
    @display(description="Auto")
    def auto_flags(self, obj: ScheduledMaintenance) -> str:
        """Display automation flags."""
        flags = []
        
        if obj.auto_enable:
            flags.append('<span style="color: green;">▶️ Start</span>')
        
        if obj.auto_disable:
            flags.append('<span style="color: blue;">⏹️ Stop</span>')
        
        if not flags:
            return '<span style="color: gray;">Manual</span>'
        
        return format_html(' '.join(flags))
    
    @action(description="Start Maintenance", variant=ActionVariant.SUCCESS)
    def start_maintenance_action(self, request: HttpRequest, queryset: Any) -> None:
        """Start selected maintenance events."""
        started = 0
        failed = 0
        
        for maintenance in queryset:
            if maintenance.status == ScheduledMaintenance.Status.SCHEDULED:
                try:
                    result = maintenance.start_maintenance()
                    if result['success']:
                        started += 1
                    else:
                        failed += 1
                except Exception as e:
                    failed += 1
                    messages.error(request, f"Failed to start {maintenance.title}: {e}")
        
        if started > 0:
            messages.success(request, f"Started {started} maintenance events")
        if failed > 0:
            messages.error(request, f"Failed to start {failed} maintenance events")
    
    @action(description="Complete Maintenance", variant=ActionVariant.PRIMARY)
    def complete_maintenance_action(self, request: HttpRequest, queryset: Any) -> None:
        """Complete selected maintenance events."""
        completed = 0
        failed = 0
        
        for maintenance in queryset:
            if maintenance.status == ScheduledMaintenance.Status.ACTIVE:
                try:
                    result = maintenance.complete_maintenance()
                    if result['success']:
                        completed += 1
                    else:
                        failed += 1
                except Exception as e:
                    failed += 1
                    messages.error(request, f"Failed to complete {maintenance.title}: {e}")
        
        if completed > 0:
            messages.success(request, f"Completed {completed} maintenance events")
        if failed > 0:
            messages.error(request, f"Failed to complete {failed} maintenance events")
    
    @action(description="Cancel Maintenance", variant=ActionVariant.DANGER)
    def cancel_maintenance_action(self, request: HttpRequest, queryset: Any) -> None:
        """Cancel selected maintenance events."""
        cancelled = 0
        
        for maintenance in queryset:
            if maintenance.status in [ScheduledMaintenance.Status.SCHEDULED, ScheduledMaintenance.Status.ACTIVE]:
                try:
                    result = maintenance.cancel_maintenance(reason="Cancelled via admin")
                    if result['success']:
                        cancelled += 1
                except Exception as e:
                    messages.error(request, f"Failed to cancel {maintenance.title}: {e}")
        
        if cancelled > 0:
            messages.success(request, f"Cancelled {cancelled} maintenance events")
    
    @action(description="Duplicate Maintenance")
    def duplicate_maintenance_action(self, request: HttpRequest, queryset: Any) -> None:
        """Duplicate selected maintenance events."""
        duplicated = 0
        
        for maintenance in queryset:
            try:
                # Create duplicate with new start time (1 week later)
                new_start = maintenance.scheduled_start + timezone.timedelta(weeks=1)
                
                duplicate = ScheduledMaintenance.objects.create(
                    title=f"{maintenance.title} (Copy)",
                    description=maintenance.description,
                    scheduled_start=new_start,
                    estimated_duration=maintenance.estimated_duration,
                    maintenance_message=maintenance.maintenance_message,
                    template=maintenance.template,
                    priority=maintenance.priority,
                    auto_enable=maintenance.auto_enable,
                    auto_disable=maintenance.auto_disable,
                    notify_before=maintenance.notify_before,
                    created_by=f"{maintenance.created_by} (duplicate)"
                )
                
                # Copy sites
                duplicate.sites.set(maintenance.sites.all())
                duplicated += 1
                
            except Exception as e:
                messages.error(request, f"Failed to duplicate {maintenance.title}: {e}")
        
        if duplicated > 0:
            messages.success(request, f"Duplicated {duplicated} maintenance events")
    
    def calendar_view(self, request: HttpRequest) -> TemplateResponse:
        """Calendar view for scheduled maintenances."""
        from ..services.scheduled_maintenance_service import scheduled_maintenance_service
        
        calendar_data = scheduled_maintenance_service.get_maintenance_calendar(days=30)
        
        context = {
            'title': 'Maintenance Calendar',
            'calendar_data': calendar_data,
            'opts': self.model._meta,
        }
        
        return TemplateResponse(
            request,
            'admin/maintenance/scheduled_maintenance_calendar.html',
            context
        )
    
    def start_maintenance_view(self, request: HttpRequest, object_id: int) -> HttpResponse:
        """Start specific maintenance event."""
        maintenance = self.get_object(request, object_id)
        
        if maintenance.status != ScheduledMaintenance.Status.SCHEDULED:
            messages.error(request, f"Cannot start maintenance in {maintenance.status} status")
        else:
            try:
                result = maintenance.start_maintenance()
                if result['success']:
                    messages.success(
                        request, 
                        f"Started maintenance '{maintenance.title}' affecting {result['sites_affected']} sites"
                    )
                else:
                    messages.error(request, f"Failed to start maintenance: {result.get('error')}")
            except Exception as e:
                messages.error(request, f"Error starting maintenance: {e}")
        
        return redirect('admin:maintenance_scheduledmaintenance_change', object_id)
    
    def complete_maintenance_view(self, request: HttpRequest, object_id: int) -> HttpResponse:
        """Complete specific maintenance event."""
        maintenance = self.get_object(request, object_id)
        
        if maintenance.status != ScheduledMaintenance.Status.ACTIVE:
            messages.error(request, f"Cannot complete maintenance in {maintenance.status} status")
        else:
            try:
                result = maintenance.complete_maintenance()
                if result['success']:
                    duration = result.get('actual_duration', 0) / 3600
                    messages.success(
                        request, 
                        f"Completed maintenance '{maintenance.title}' (duration: {duration:.1f}h)"
                    )
                else:
                    messages.error(request, f"Failed to complete maintenance: {result.get('error')}")
            except Exception as e:
                messages.error(request, f"Error completing maintenance: {e}")
        
        return redirect('admin:maintenance_scheduledmaintenance_change', object_id)
