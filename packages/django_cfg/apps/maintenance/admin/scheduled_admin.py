"""
ScheduledMaintenance Admin v2.0 - NEW Declarative Pydantic Approach

Enhanced scheduled maintenance management with Material Icons and auto-generated displays.
"""

from django.contrib import admin
from django.db.models import Count, Q
from django.utils import timezone

from django_cfg.modules.django_admin import (
    ActionConfig,
    AdminConfig,
    BadgeField,
    BooleanField,
    CurrencyField,
    DateTimeField,
    FieldsetConfig,
    Icons,
    TextField,
    UserField
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from ..models import ScheduledMaintenance


# ===== ScheduledMaintenance Admin Config =====

scheduled_maintenance_config = AdminConfig(
    model=ScheduledMaintenance,

    # List display
    list_display=[
        "status",
        "title",
        "scheduled_start",
        "duration_minutes",
        "sites_count",
        "priority",
        "auto_flags",
        "created_at",
    ],

    # Display fields with UI widgets (auto-generates display methods)
    display_fields=[
        BadgeField(
            name="status",
            title="Status",
            label_map={
                "scheduled": "warning",
                "active": "info",
                "completed": "success",
                "cancelled": "secondary",
                "failed": "danger"
            },
            icon=Icons.SCHEDULE
        ),
        BadgeField(
            name="title",
            title="Title",
            variant="primary",
            icon=Icons.EVENT,
            ordering="title",
            header=True
        ),
        DateTimeField(
            name="scheduled_start",
            title="Scheduled Start",
            ordering="scheduled_start"
        ),
        TextField(
            name="duration_minutes",
            title="Duration"
        ),
        TextField(
            name="sites_count",
            title="Sites"
        ),
        BadgeField(
            name="priority",
            title="Priority",
            label_map={
                "low": "secondary",
                "medium": "info",
                "high": "warning",
                "critical": "danger"
            },
            icon=Icons.PRIORITY_HIGH
        ),
        TextField(
            name="auto_flags",
            title="Auto Flags"
        ),
        DateTimeField(
            name="created_at",
            title="Created",
            ordering="created_at"
        ),
    ],

    # Search and filters
    search_fields=["title", "description", "maintenance_message"],
    list_filter=[
        "status",
        "priority",
        "auto_enable",
        "auto_disable",
        "scheduled_start",
        "created_at"
    ],

    # Readonly fields
    readonly_fields=[
        "created_at",
        "updated_at"
    ],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="Basic Information",
            fields=["title", "description"]
        ),
        FieldsetConfig(
            title="Scheduling",
            fields=["scheduled_start", "duration_minutes"]
        ),
        FieldsetConfig(
            title="Sites",
            fields=["sites"]
        ),
        FieldsetConfig(
            title="Settings",
            fields=["priority", "auto_enable", "auto_disable"]
        ),
        FieldsetConfig(
            title="Messages",
            fields=["maintenance_message"],
            collapsed=True
        ),
        FieldsetConfig(
            title="Status",
            fields=["status"]
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=["created_at", "updated_at"],
            collapsed=True
        ),
    ],

    # Actions
    actions=[
        ActionConfig(
            name="execute_maintenance",
            description="Execute maintenance",
            variant="info",
            handler="django_cfg.apps.maintenance.admin.actions.execute_maintenance"
        ),
        ActionConfig(
            name="cancel_maintenance",
            description="Cancel maintenance",
            variant="warning",
            handler="django_cfg.apps.maintenance.admin.actions.cancel_maintenance"
        ),
        ActionConfig(
            name="reschedule_maintenance",
            description="Reschedule maintenance",
            variant="primary",
            handler="django_cfg.apps.maintenance.admin.actions.reschedule_maintenance"
        ),
    ],

    # Ordering
    ordering=["-scheduled_start"],
)


@admin.register(ScheduledMaintenance)
class ScheduledMaintenanceAdmin(PydanticAdmin):
    """Admin for ScheduledMaintenance using Django Admin Utilities v2.0."""
    config = scheduled_maintenance_config

    filter_horizontal = ["sites"]

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
