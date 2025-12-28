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

from ..models import (
    GRPCRequestLog,
    GRPCServerStatus,
    GrpcApiKey,
    GrpcAgentConnectionState,
    GrpcAgentConnectionEvent,
    GrpcAgentConnectionMetric,
)


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
        "performance_stats_display",
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
        "uptime_display",
        "server_config_display",
        "process_info_display",
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
    select_related=["user"],

    # List display
    list_display=[
        "status_indicator",
        "name",
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
        UserField(name="user", title="User", header=True, ordering="user__username"),
        DateTimeField(name="last_used_at", title="Last Used", ordering="last_used_at"),
        DateTimeField(name="created_at", title="Created", ordering="created_at"),
    ],

    # Filters
    list_filter=["is_active", "created_at", "expires_at", "user"],
    search_fields=["name", "description", "user__username", "user__email", "key"],

    # Readonly fields
    readonly_fields=[
        "key_display",
        "masked_key",
        "request_count",
        "last_used_at",
        "created_at",
        "updated_at",
    ],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="Basic Information",
            fields=["name", "description", "is_active"],
        ),
        FieldsetConfig(
            title="API Key",
            fields=["key_display", "masked_key"],
        ),
        FieldsetConfig(
            title="User Association",
            fields=["user"],
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


# Declarative configuration for GrpcAgentConnectionState
grpcagentconnectionstate_config = AdminConfig(
    model=GrpcAgentConnectionState,

    # List display
    list_display=[
        "machine_name",
        "machine_id",
        "status",
        "last_known_ip",
        "client_version",
        "current_rtt_ms",
        "current_packet_loss_percent",
        "last_connected_at",
        "consecutive_error_count",
    ],

    # Auto-generated display methods
    display_fields=[
        TextField(name="machine_name", title="Machine", ordering="machine_name"),
        TextField(name="machine_id", title="Machine ID", ordering="machine_id"),
        BadgeField(
            name="status",
            title="Status",
            label_map={
                "connected": "success",
                "disconnected": "secondary",
                "reconnecting": "warning",
                "error": "danger",
                "unknown": "info",
            },
            icon=Icons.WIFI,
        ),
        DateTimeField(name="last_connected_at", title="Last Connected", ordering="last_connected_at"),
        DateTimeField(name="last_disconnected_at", title="Last Disconnected", ordering="last_disconnected_at"),
        DateTimeField(name="first_connected_at", title="First Connected", ordering="first_connected_at"),
    ],

    # Filters
    list_filter=["status", "last_connected_at", "first_connected_at"],
    search_fields=["machine_id", "machine_name", "last_known_ip", "client_version"],

    # Readonly fields
    readonly_fields=[
        "id",
        "first_connected_at",
        "created_at",
        "updated_at",
    ],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="Machine Identity",
            fields=["machine_id", "machine_name", "status"],
        ),
        FieldsetConfig(
            title="Network",
            fields=["last_known_ip", "client_version"],
        ),
        FieldsetConfig(
            title="Connection Times",
            fields=["first_connected_at", "last_connected_at", "last_disconnected_at"],
        ),
        FieldsetConfig(
            title="Metrics",
            fields=["current_rtt_ms", "current_packet_loss_percent"],
        ),
        FieldsetConfig(
            title="Errors",
            fields=["last_error_message", "last_error_at", "consecutive_error_count"],
            collapsed=True,
        ),
    ],

    # Date hierarchy
    date_hierarchy="last_connected_at",

    # Ordering
    ordering=["-last_connected_at"],

    # Per page
    list_per_page=50,
)


# Declarative configuration for GrpcAgentConnectionEvent
grpcagentconnectionevent_config = AdminConfig(
    model=GrpcAgentConnectionEvent,

    # Performance optimization
    select_related=["connection_state"],

    # List display
    list_display=[
        "connection_state",
        "event_type",
        "timestamp",
        "ip_address",
        "client_version",
        "duration_seconds",
        "error_message_short",
    ],

    # Auto-generated display methods
    display_fields=[
        BadgeField(
            name="event_type",
            title="Event",
            label_map={
                "connected": "success",
                "disconnected": "secondary",
                "reconnecting": "warning",
                "error": "danger",
            },
            icon=Icons.NOTIFICATIONS,
        ),
        DateTimeField(name="timestamp", title="Time", ordering="timestamp"),
    ],

    # Filters
    list_filter=["event_type", "timestamp", "connection_state"],
    search_fields=[
        "connection_state__machine_id",
        "connection_state__machine_name",
        "ip_address",
        "error_message",
        "error_code",
    ],

    # Readonly fields
    readonly_fields=["id", "timestamp"],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="Event",
            fields=["connection_state", "event_type", "timestamp"],
        ),
        FieldsetConfig(
            title="Context",
            fields=["ip_address", "client_version", "duration_seconds"],
        ),
        FieldsetConfig(
            title="Error Details",
            fields=["error_message", "error_code", "error_details"],
            collapsed=True,
        ),
    ],

    # Date hierarchy
    date_hierarchy="timestamp",

    # Ordering
    ordering=["-timestamp"],

    # Per page
    list_per_page=100,
)


# Declarative configuration for GrpcAgentConnectionMetric
grpcagentconnectionmetric_config = AdminConfig(
    model=GrpcAgentConnectionMetric,

    # Performance optimization
    select_related=["connection_state"],

    # List display
    list_display=[
        "connection_state",
        "timestamp",
        "health_status",
        "rtt_mean_ms",
        "packet_loss_percent",
        "keepalive_sent",
        "keepalive_timeout",
        "active_streams",
        "failed_streams",
    ],

    # Auto-generated display methods
    display_fields=[
        BadgeField(
            name="health_status",
            title="Health",
            label_map={
                "healthy": "success",
                "degraded": "warning",
                "poor": "danger",
                "unknown": "secondary",
            },
            icon=Icons.HEALTH_AND_SAFETY,
        ),
        DateTimeField(name="timestamp", title="Time", ordering="timestamp"),
    ],

    # Filters
    list_filter=["health_status", "timestamp", "connection_state"],
    search_fields=[
        "connection_state__machine_id",
        "connection_state__machine_name",
    ],

    # Readonly fields
    readonly_fields=["id", "timestamp"],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="Connection",
            fields=["connection_state", "timestamp", "health_status", "sample_window_seconds"],
        ),
        FieldsetConfig(
            title="Latency (RTT)",
            fields=["rtt_min_ms", "rtt_max_ms", "rtt_mean_ms", "rtt_stddev_ms"],
        ),
        FieldsetConfig(
            title="Packet Loss",
            fields=["packet_loss_percent", "packets_sent", "packets_received"],
        ),
        FieldsetConfig(
            title="Keepalive",
            fields=["keepalive_sent", "keepalive_ack", "keepalive_timeout"],
        ),
        FieldsetConfig(
            title="Streams",
            fields=["active_streams", "failed_streams"],
        ),
    ],

    # Date hierarchy
    date_hierarchy="timestamp",

    # Ordering
    ordering=["-timestamp"],

    # Per page
    list_per_page=100,
)


__all__ = [
    "grpcrequestlog_config",
    "grpcserverstatus_config",
    "grpcapikey_config",
    "grpcagentconnectionstate_config",
    "grpcagentconnectionevent_config",
    "grpcagentconnectionmetric_config",
]
