"""
Leads Admin v2.0 - NEW Declarative Pydantic Approach

Clean lead management with auto-generated display methods.
"""

from django.contrib import admin
from django.db.models import Count, Q
from unfold.contrib.filters.admin import AutocompleteSelectFilter

from django_cfg.modules.django_admin import (
    ActionConfig,
    AdminConfig,
    BadgeField,
    DateTimeField,
    FieldsetConfig,
    Icons,
    TextField,
    UserField,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from ..models import Lead
from .resources import LeadResource
from .actions import mark_as_contacted, mark_as_qualified, mark_as_converted, mark_as_rejected


# ===== Lead Admin Config =====

lead_config = AdminConfig(
    model=Lead,

    # Performance optimization
    select_related=['user'],

    # Import/Export
    import_export_enabled=True,
    resource_class=LeadResource,

    # List display
    list_display=[
        "name",
        "email",
        "company",
        "contact_type",
        "contact_value",
        "subject",
        "status",
        "user",
        "created_at"
    ],

    # Display fields with UI widgets (auto-generates display methods)
    display_fields=[
        BadgeField(
            name="name",
            title="Name",
            variant="primary",
            icon=Icons.PERSON,
            header=True
        ),
        BadgeField(
            name="email",
            title="Email",
            variant="info",
            icon=Icons.EMAIL
        ),
        BadgeField(
            name="company",
            title="Company",
            variant="secondary",
            icon=Icons.BUSINESS,
            empty_value="—"
        ),
        BadgeField(
            name="contact_type",
            title="Contact Type",
            variant="secondary",
            icon=Icons.CONTACT_PHONE,
            label_map={
                "email": "info",
                "phone": "success",
                "telegram": "primary",
                "whatsapp": "success",
                "other": "secondary"
            }
        ),
        TextField(
            name="contact_value",
            title="Contact Value",
            empty_value="—"
        ),
        TextField(
            name="subject",
            title="Subject",
            empty_value="—"
        ),
        BadgeField(
            name="status",
            title="Status",
            label_map={
                "new": "info",
                "contacted": "warning",
                "qualified": "primary",
                "converted": "success",
                "rejected": "danger"
            }
        ),
        UserField(
            name="user",
            title="Assigned User",
            empty_value="—"
        ),
        DateTimeField(
            name="created_at",
            title="Created",
            ordering="created_at"
        ),
    ],

    # Search and filters
    search_fields=["name", "email", "company", "company_site", "message", "subject", "admin_notes"],
    list_filter=[
        "status",
        "contact_type",
        "company",
        "created_at",
        ("user", AutocompleteSelectFilter)
    ],

    # Readonly fields
    readonly_fields=["created_at", "updated_at", "ip_address", "user_agent"],

    # Autocomplete fields
    autocomplete_fields=["user"],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="Basic Information",
            fields=["name", "email", "company", "company_site"]
        ),
        FieldsetConfig(
            title="Contact Information",
            fields=["contact_type", "contact_value"]
        ),
        FieldsetConfig(
            title="Message",
            fields=["subject", "message", "extra"]
        ),
        FieldsetConfig(
            title="Metadata",
            fields=["site_url", "ip_address", "user_agent"],
            collapsed=True
        ),
        FieldsetConfig(
            title="Status and Processing",
            fields=["status", "user", "admin_notes"]
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
            name="mark_as_contacted",
            description="Mark as contacted",
            variant="warning",
            handler=mark_as_contacted
        ),
        ActionConfig(
            name="mark_as_qualified",
            description="Mark as qualified",
            variant="primary",
            handler=mark_as_qualified
        ),
        ActionConfig(
            name="mark_as_converted",
            description="Mark as converted",
            variant="success",
            handler=mark_as_converted
        ),
        ActionConfig(
            name="mark_as_rejected",
            description="Mark as rejected",
            variant="danger",
            handler=mark_as_rejected
        ),
    ],

    # Ordering
    ordering=["-created_at"],
    list_per_page=50,
    date_hierarchy="created_at",
)


# ===== Lead Admin Class =====

@admin.register(Lead)
class LeadAdmin(PydanticAdmin):
    """
    Lead admin using NEW Pydantic declarative approach.

    Features:
    - Auto-generated display methods from FieldConfig
    - Declarative actions with ActionConfig
    - Import/Export functionality
    - Material Icons integration
    - Clean minimal code
    """
    config = lead_config

    # Custom changelist view for statistics
    def changelist_view(self, request, extra_context=None):
        """Add lead statistics to changelist."""
        extra_context = extra_context or {}

        queryset = self.get_queryset(request)
        stats = queryset.aggregate(
            total_leads=Count('id'),
            new_leads=Count('id', filter=Q(status='new')),
            contacted_leads=Count('id', filter=Q(status='contacted')),
            qualified_leads=Count('id', filter=Q(status='qualified')),
            converted_leads=Count('id', filter=Q(status='converted')),
            rejected_leads=Count('id', filter=Q(status='rejected'))
        )

        # Contact type breakdown
        contact_type_counts = dict(
            queryset.values_list('contact_type').annotate(
                count=Count('id')
            )
        )

        # Company breakdown (top 10)
        company_counts = dict(
            queryset.exclude(company__isnull=True).exclude(company='')
            .values_list('company').annotate(count=Count('id'))
            .order_by('-count')[:10]
        )

        extra_context['lead_stats'] = {
            'total_leads': stats['total_leads'] or 0,
            'new_leads': stats['new_leads'] or 0,
            'contacted_leads': stats['contacted_leads'] or 0,
            'qualified_leads': stats['qualified_leads'] or 0,
            'converted_leads': stats['converted_leads'] or 0,
            'rejected_leads': stats['rejected_leads'] or 0,
            'contact_type_counts': contact_type_counts,
            'company_counts': company_counts
        }

        return super().changelist_view(request, extra_context)
