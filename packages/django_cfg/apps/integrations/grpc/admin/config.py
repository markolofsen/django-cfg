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

from ..models import GRPCRequestLog, GRPCServerStatus


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


# Declarative configuration for GRPCServerStatus
grpcserverstatus_config = AdminConfig(
    model=GRPCServerStatus,

    # List display
    list_display=[
        "instance_id",
        "address",
        "status_badge",
        "pid",
        "hostname",
        "uptime_display",
        "started_at",
        "last_heartbeat",
    ],

    # Auto-generated display methods
    display_fields=[
        BadgeField(
            name="status",
            title="Status",
            label_map={
                "starting": "info",
                "running": "success",
                "stopping": "warning",
                "stopped": "secondary",
                "error": "danger",
            },
            icon=Icons.CHECK_CIRCLE,
        ),
        DateTimeField(name="started_at", title="Started", ordering="started_at"),
        DateTimeField(name="last_heartbeat", title="Last Heartbeat", ordering="last_heartbeat"),
        DateTimeField(name="stopped_at", title="Stopped", ordering="stopped_at"),
    ],

    # Filters
    list_filter=["status", "hostname", "started_at"],
    search_fields=[
        "instance_id",
        "address",
        "hostname",
        "pid",
    ],

    # Readonly fields
    readonly_fields=[
        "id",
        "instance_id",
        "started_at",
        "last_heartbeat",
        "stopped_at",
        "created_at",
        "updated_at",
        "uptime_display",
        "is_running",
    ],

    # Date hierarchy
    date_hierarchy="started_at",

    # Per page
    list_per_page=50,

    # Ordering
    ordering=["-started_at"],
)


__all__ = ["grpcrequestlog_config", "grpcserverstatus_config"]
