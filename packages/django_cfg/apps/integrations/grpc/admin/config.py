"""
Admin configuration for gRPC models.

Declarative AdminConfig using PydanticAdmin patterns.
"""

from django_cfg.modules.django_admin import (
    AdminConfig,
    BadgeField,
    BooleanField,
    DateTimeField,
    FieldsetConfig,
    Icons,
    TextField,
    UserField,
)

from ..models import GRPCRequestLog, GRPCServerStatus, GrpcApiKey


# Declarative configuration for GRPCRequestLog
grpcrequestlog_config = AdminConfig(
    model=GRPCRequestLog,
    # Performance optimization
    select_related=["user", "api_key"],

    # List display
    list_display=[
        "service_badge",
        "method_badge",
        "status",
        "grpc_status_code_display",
        "user",
        "api_key_display",
        "duration_display",
        "created_at",
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
    list_filter=["status", "grpc_status_code", "service_name", "method_name", "is_authenticated", "api_key", "created_at"],
    search_fields=[
        "request_id",
        "service_name",
        "method_name",
        "full_method",
        "user__username",
        "user__email",
        "api_key__name",
        "api_key__key",
        "error_message",
        "client_ip",
    ],
    # Autocomplete for user and api_key fields
    autocomplete_fields=["user", "api_key"],
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
        "status",
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
        "server_config_display",
        "process_info_display",
        "registered_services_display",
        "error_display",
        "lifecycle_display",
    ],

    # Date hierarchy
    date_hierarchy="started_at",

    # Per page
    list_per_page=50,

    # Ordering
    ordering=["-started_at"],
)


# Declarative configuration for GrpcApiKey
grpcapikey_config = AdminConfig(
    model=GrpcApiKey,

    # Performance optimization
    select_related=["user", "created_by"],

    # List display
    list_display=[
        "status_indicator",
        "name",
        "key_type",
        "user",
        "masked_key_display",
        "request_count_display",
        "last_used_at",
        "expires_display",
        "created_at",
    ],

    # Auto-generated display methods
    display_fields=[
        TextField(name="name", title="Name", ordering="name"),
        BadgeField(
            name="key_type",
            title="Type",
            label_map={
                "service": "info",
                "cli": "primary",
                "webhook": "warning",
                "internal": "secondary",
                "development": "danger",
            },
        ),
        UserField(name="user", title="User", header=True, ordering="user__username"),
        DateTimeField(name="last_used_at", title="Last Used", ordering="last_used_at"),
        DateTimeField(name="created_at", title="Created", ordering="created_at"),
    ],

    # Filters
    list_filter=["is_active", "key_type", "created_at", "expires_at", "user"],
    search_fields=["name", "description", "user__username", "user__email", "key"],

    # Readonly fields
    readonly_fields=[
        "key_display",
        "masked_key",
        "request_count",
        "last_used_at",
        "created_at",
        "updated_at",
        "created_by",
    ],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="Basic Information",
            fields=["name", "description", "key_type", "is_active"],
        ),
        FieldsetConfig(
            title="API Key",
            fields=["key_display", "masked_key"],
        ),
        FieldsetConfig(
            title="User Association",
            fields=["user", "created_by"],
        ),
        FieldsetConfig(
            title="Expiration",
            fields=["expires_at"],
        ),
        FieldsetConfig(
            title="Usage Statistics",
            fields=["request_count", "last_used_at"],
            collapsed=True,
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=["created_at", "updated_at"],
            collapsed=True,
        ),
    ],

    # Autocomplete for user field
    autocomplete_fields=["user"],

    # Ordering
    ordering=["-created_at"],

    # Per page
    list_per_page=50,
)


__all__ = ["grpcrequestlog_config", "grpcserverstatus_config", "grpcapikey_config"]
