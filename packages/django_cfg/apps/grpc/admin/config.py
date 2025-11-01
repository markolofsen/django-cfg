"""
Admin configuration for gRPC models.

Declarative AdminConfig using PydanticAdmin patterns.
"""

from django_cfg.modules.django_admin import (
    AdminConfig,
    BadgeField,
    DateTimeField,
    Icons,
    UserField,
)

from ..models import GRPCRequestLog


# Declarative configuration for GRPCRequestLog
grpcrequestlog_config = AdminConfig(
    model=GRPCRequestLog,
    # Performance optimization
    select_related=["user"],

    # List display
    list_display=[
        "full_method",
        "service_badge",
        "method_badge",
        "status",
        "grpc_status_code_display",
        "user",
        "duration_display",
        "created_at",
        "completed_at"
    ],

    # Auto-generated display methods
    display_fields=[
        BadgeField(name="service_name", title="Service", variant="info", icon=Icons.API),
        BadgeField(name="method_name", title="Method", variant="secondary", icon=Icons.CODE),
        BadgeField(
            name="status",
            title="Status",
            label_map={
                "pending": "warning",
                "success": "success",
                "error": "danger",
                "cancelled": "secondary",
                "timeout": "danger",
            },
        ),
        UserField(name="user", title="User", header=True),
        DateTimeField(name="created_at", title="Created", ordering="created_at"),
        DateTimeField(name="completed_at", title="Completed", ordering="completed_at"),
    ],
    # Filters
    list_filter=["status", "grpc_status_code", "service_name", "method_name", "is_authenticated", "created_at"],
    search_fields=[
        "request_id",
        "service_name",
        "method_name",
        "full_method",
        "user__username",
        "user__email",
        "error_message",
        "client_ip",
    ],
    # Autocomplete for user field
    autocomplete_fields=["user"],
    # Readonly fields
    readonly_fields=[
        "id",
        "request_id",
        "created_at",
        "completed_at",
        "request_data_display",
        "response_data_display",
        "error_details_display",
        "performance_stats_display",
        "client_info_display",
    ],
    # Date hierarchy
    date_hierarchy="created_at",
    # Per page
    list_per_page=50,
)


__all__ = ["grpcrequestlog_config"]
