"""
MaintenanceLog Admin v2.0 - NEW Declarative Pydantic Approach

Read-only admin interface for viewing maintenance operation logs.
"""

import json

from django.contrib import admin
from django.db.models import Count, Q

from django_cfg.modules.django_admin import (
    AdminConfig,
    BadgeField,
    BooleanField,
    CurrencyField,
    DateTimeField,
    FieldsetConfig,
    Icons,
    TextField,
    UserField,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from ..models import MaintenanceLog


# ===== MaintenanceLog Admin Config =====

maintenancelog_config = AdminConfig(
    model=MaintenanceLog,

    # Performance optimization
    select_related=['site'],

    # List display
    list_display=[
        'status',
        'site',
        'action',
        'created_at',
        'duration_seconds',
        'error_message'
    ],

    # Display fields with UI widgets (auto-generates display methods)
    display_fields=[
        BadgeField(
            name="status",
            title="Status",
            label_map={
                "success": "success",
                "failed": "danger",
                "pending": "warning"
            },
            icon=Icons.CHECK_CIRCLE
        ),
        BadgeField(
            name="site",
            title="Site",
            variant="info",
            icon=Icons.LANGUAGE,
            ordering="site__name",
            header=True
        ),
        BadgeField(
            name="action",
            title="Action",
            label_map={
                "enable": "warning",
                "disable": "success",
                "check_status": "info"
            },
            icon=Icons.BUILD
        ),
        DateTimeField(
            name="created_at",
            title="Created",
            ordering="created_at"
        ),
        TextField(
            name="duration_seconds",
            title="Duration",
            empty_value="—"
        ),
        TextField(
            name="error_message",
            title="Error",
            empty_value="—"
        ),
    ],

    # Search and filters
    search_fields=[
        'site__name',
        'site__domain',
        'reason',
        'error_message'
    ],
    list_filter=[
        'action',
        'status',
        'created_at',
        'site'
    ],

    # Readonly fields
    readonly_fields=[
        'site',
        'action',
        'status',
        'reason',
        'error_message',
        'cloudflare_response',
        'created_at',
        'duration_seconds',
        'cloudflare_response_formatted'
    ],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title='Log Information',
            fields=['site', 'action', 'status', 'reason']
        ),
        FieldsetConfig(
            title='Timing',
            fields=['created_at', 'duration_seconds']
        ),
        FieldsetConfig(
            title='Error Details',
            fields=['error_message'],
            collapsed=True
        ),
        FieldsetConfig(
            title='Cloudflare Response',
            fields=['cloudflare_response_formatted'],
            collapsed=True
        )
    ],

    # Ordering
    ordering=['-created_at'],
)


@admin.register(MaintenanceLog)
class MaintenanceLogAdmin(PydanticAdmin):
    """Admin interface for MaintenanceLog model using Django Admin Utilities v2.0."""
    config = maintenancelog_config

    def has_add_permission(self, request):
        """Disable adding new logs through admin."""
        return False

    def has_change_permission(self, request, obj=None):
        """Disable editing logs through admin."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow deleting old logs."""
        return True

    # Custom readonly method for detail view
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
