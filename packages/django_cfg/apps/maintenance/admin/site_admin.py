"""
CloudflareSite Admin v2.0 - NEW Declarative Pydantic Approach

Enhanced site management with Material Icons and auto-generated displays.
"""

from django.contrib import admin
from django.db.models import Count, Q
from unfold.admin import TabularInline

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
    UserField,
    computed_field
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from ..models import CloudflareSite, MaintenanceLog


class MaintenanceLogInline(TabularInline):
    """Inline for recent maintenance logs."""

    model = MaintenanceLog
    verbose_name = "Recent Log"
    verbose_name_plural = "Recent Maintenance Logs"
    extra = 0
    max_num = 5
    can_delete = False
    show_change_link = True

    fields = ['status_display', 'action', 'created_at', 'duration_seconds', 'error_preview']
    readonly_fields = ['status_display', 'action', 'created_at', 'duration_seconds', 'error_preview']

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @computed_field("Status")
    def status_display(self, obj):
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

        return self.html.badge(obj.get_status_display(), variant=variant, icon=icon)

    @computed_field("Error")
    def error_preview(self, obj):
        """Show error message preview."""
        if not obj.error_message:
            return "—"

        preview = obj.error_message[:50]
        if len(obj.error_message) > 50:
            preview += "..."

        return preview


# ===== CloudflareSite Admin Config =====

cloudflare_site_config = AdminConfig(
    model=CloudflareSite,

    # Performance optimization
    select_related=['api_key'],

    # List display
    list_display=[
        'status',
        'name',
        'domain',
        'subdomain_config',
        'maintenance_active',
        'is_active',
        'last_maintenance_at',
        'logs_count',
        'api_key'
    ],

    # Display fields with UI widgets (auto-generates display methods)
    display_fields=[
        BadgeField(
            name="status",
            title="Status",
            label_map={
                "maintenance": "warning",
                "active": "success",
                "inactive": "secondary"
            },
            icon=Icons.LANGUAGE
        ),
        BadgeField(
            name="name",
            title="Name",
            variant="primary",
            icon=Icons.LANGUAGE,
            ordering="name",
            header=True
        ),
        BadgeField(
            name="domain",
            title="Domain",
            variant="info",
            icon=Icons.PUBLIC,
            ordering="domain"
        ),
        TextField(
            name="subdomain_config",
            title="Subdomains"
        ),
        BooleanField(
            name="maintenance_active",
            title="Maintenance"
        ),
        BooleanField(
            name="is_active",
            title="Active"
        ),
        DateTimeField(
            name="last_maintenance_at",
            title="Last Maintenance",
            empty_value="Never"
        ),
        TextField(
            name="logs_count",
            title="Logs"
        ),
        TextField(
            name="api_key",
            title="API Key",
            empty_value="—"
        ),
    ],

    # Search and filters
    search_fields=['name', 'domain', 'zone_id'],
    list_filter=[
        'maintenance_active',
        'is_active',
        'include_subdomains',
        'created_at',
        'last_maintenance_at'
    ],

    # Readonly fields
    readonly_fields=[
        'created_at',
        'updated_at',
        'last_maintenance_at',
        'logs_preview'
    ],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title='Site Information',
            fields=['name', 'domain', 'zone_id']
        ),
        FieldsetConfig(
            title='Maintenance Configuration',
            fields=['maintenance_url', 'include_subdomains']
        ),
        FieldsetConfig(
            title='Cloudflare Settings',
            fields=['api_key']
        ),
        FieldsetConfig(
            title='Status',
            fields=['is_active', 'maintenance_active']
        ),
        FieldsetConfig(
            title='Timestamps',
            fields=['created_at', 'updated_at', 'last_maintenance_at'],
            collapsed=True
        ),
        FieldsetConfig(
            title='Recent Logs',
            fields=['logs_preview'],
            collapsed=True
        )
    ],

    # Actions
    actions=[
        ActionConfig(
            name="enable_maintenance",
            description="Enable maintenance mode",
            variant="warning",
            handler="django_cfg.apps.maintenance.admin.actions.enable_maintenance_mode"
        ),
        ActionConfig(
            name="disable_maintenance",
            description="Disable maintenance mode",
            variant="success",
            handler="django_cfg.apps.maintenance.admin.actions.disable_maintenance_mode"
        ),
        ActionConfig(
            name="activate_sites",
            description="Activate sites",
            variant="success",
            handler="django_cfg.apps.maintenance.admin.actions.activate_sites"
        ),
        ActionConfig(
            name="deactivate_sites",
            description="Deactivate sites",
            variant="warning",
            handler="django_cfg.apps.maintenance.admin.actions.deactivate_sites"
        ),
        ActionConfig(
            name="sync_with_cloudflare",
            description="Sync with Cloudflare",
            variant="info",
            handler="django_cfg.apps.maintenance.admin.actions.sync_with_cloudflare"
        ),
    ],

    # Ordering
    ordering=['-created_at'],
)


@admin.register(CloudflareSite)
class CloudflareSiteAdmin(PydanticAdmin):
    """Admin for CloudflareSite using Django Admin Utilities v2.0."""
    config = cloudflare_site_config

    inlines = [MaintenanceLogInline]

    # Custom readonly methods for detail view
    def logs_preview(self, obj: CloudflareSite) -> str:
        """Show recent maintenance logs."""
        logs = obj.maintenancelog_set.all()[:5]

        if not logs:
            return "No maintenance logs yet"

        log_list = []
        for log in logs:
            status_text = "Success" if log.status == MaintenanceLog.Status.SUCCESS else "Failed" if log.status == MaintenanceLog.Status.FAILED else "Pending"
            log_list.append(f"{status_text} {log.action} - {log.created_at.strftime('%Y-%m-%d %H:%M')}")

        return "\n".join(log_list)
    logs_preview.short_description = "Recent Logs"

    def changelist_view(self, request, extra_context=None):
        """Add site statistics to changelist."""
        extra_context = extra_context or {}

        queryset = self.get_queryset(request)
        stats = queryset.aggregate(
            total_sites=Count('id'),
            active_sites=Count('id', filter=Q(is_active=True)),
            maintenance_sites=Count('id', filter=Q(maintenance_active=True)),
            subdomain_sites=Count('id', filter=Q(include_subdomains=True))
        )

        extra_context['site_stats'] = {
            'total_sites': stats['total_sites'] or 0,
            'active_sites': stats['active_sites'] or 0,
            'maintenance_sites': stats['maintenance_sites'] or 0,
            'subdomain_sites': stats['subdomain_sites'] or 0
        }

        return super().changelist_view(request, extra_context)
