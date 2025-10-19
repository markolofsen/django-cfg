"""
CloudflareApiKey Admin v2.0 - NEW Declarative Pydantic Approach

Enhanced API key management with Material Icons and auto-generated displays.
"""

from django.contrib import admin
from django.db.models import Count, Q

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

from ..models import CloudflareApiKey


# ===== CloudflareApiKey Admin Config =====

cloudflare_apikey_config = AdminConfig(
    model=CloudflareApiKey,

    # List display
    list_display=[
        'status',
        'name',
        'description',
        'is_active',
        'is_default',
        'sites_count',
        'last_used_at',
        'created_at'
    ],

    # Display fields with UI widgets (auto-generates display methods)
    display_fields=[
        BadgeField(
            name="status",
            title="Status",
            label_map={
                "active_default": "success",
                "active": "success",
                "inactive": "danger"
            },
            icon=Icons.KEY
        ),
        BadgeField(
            name="name",
            title="Name",
            variant="primary",
            icon=Icons.KEY,
            ordering="name",
            header=True
        ),
        TextField(
            name="description",
            title="Description",
            empty_value="—"
        ),
        BooleanField(
            name="is_active",
            title="Active"
        ),
        BadgeField(
            name="is_default",
            title="Default",
            variant="primary",
            icon=Icons.STAR,
            empty_value="—"
        ),
        TextField(
            name="sites_count",
            title="Sites"
        ),
        DateTimeField(
            name="last_used_at",
            title="Last Used",
            empty_value="Never"
        ),
        DateTimeField(
            name="created_at",
            title="Created",
            ordering="created_at"
        ),
    ],

    # Search and filters
    search_fields=['name', 'description', 'account_id'],
    list_filter=[
        'is_active',
        'is_default',
        'created_at',
        'last_used_at'
    ],

    # Readonly fields
    readonly_fields=[
        'created_at',
        'updated_at',
        'last_used_at',
        'sites_using_key'
    ],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title='Basic Information',
            fields=['name', 'description']
        ),
        FieldsetConfig(
            title='Cloudflare Configuration',
            fields=['api_token', 'account_id'],
            collapsed=True
        ),
        FieldsetConfig(
            title='Settings',
            fields=['is_active', 'is_default']
        ),
        FieldsetConfig(
            title='Timestamps',
            fields=['created_at', 'updated_at', 'last_used_at'],
            collapsed=True
        ),
        FieldsetConfig(
            title='Usage',
            fields=['sites_using_key'],
            collapsed=True
        )
    ],

    # Actions
    actions=[
        ActionConfig(
            name="make_default",
            description="Make default API key",
            variant="primary",
            handler="django_cfg.apps.maintenance.admin.actions.make_default_key"
        ),
        ActionConfig(
            name="activate_keys",
            description="Activate API keys",
            variant="success",
            handler="django_cfg.apps.maintenance.admin.actions.activate_keys"
        ),
        ActionConfig(
            name="deactivate_keys",
            description="Deactivate API keys",
            variant="warning",
            handler="django_cfg.apps.maintenance.admin.actions.deactivate_keys"
        ),
    ],

    # Ordering
    ordering=['-created_at'],
)


@admin.register(CloudflareApiKey)
class CloudflareApiKeyAdmin(PydanticAdmin):
    """Admin interface for CloudflareApiKey model using Django Admin Utilities v2.0."""
    config = cloudflare_apikey_config

    # Custom readonly methods for detail view
    def sites_using_key(self, obj: CloudflareApiKey) -> str:
        """Show sites using this API key."""
        sites = obj.cloudflaresite_set.all()[:10]

        if not sites:
            return "No sites using this key"

        site_list = []
        for site in sites:
            status_emoji = "Maintenance" if site.maintenance_active else "Active"
            site_list.append(f"{status_emoji} {site.name} ({site.domain})")

        result = "\n".join(site_list)

        total_count = obj.cloudflaresite_set.count()
        if total_count > 10:
            result += f"\n... and {total_count - 10} more sites"

        return result
    sites_using_key.short_description = "Sites Using This Key"

    def changelist_view(self, request, extra_context=None):
        """Add API key statistics to changelist."""
        extra_context = extra_context or {}

        queryset = self.get_queryset(request)
        stats = queryset.aggregate(
            total_keys=Count('id'),
            active_keys=Count('id', filter=Q(is_active=True)),
            default_keys=Count('id', filter=Q(is_default=True))
        )

        extra_context['api_key_stats'] = {
            'total_keys': stats['total_keys'] or 0,
            'active_keys': stats['active_keys'] or 0,
            'default_keys': stats['default_keys'] or 0
        }

        return super().changelist_view(request, extra_context)
