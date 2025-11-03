"""
Admin configuration for Centrifugo models.

Declarative AdminConfig using PydanticAdmin patterns.
"""

from django_cfg.modules.django_admin import (
    AdminConfig,
    BadgeField,
    DateTimeField,
    Icons,
    UserField,
)

from ..models import CentrifugoLog


# Declarative configuration for CentrifugoLog
centrifugolog_config = AdminConfig(
    model=CentrifugoLog,
    # Performance optimization
    select_related=["user"],

    # List display
    list_display=[
        "channel",
        "type_badge",
        "status",
        "user",
        "acks_display",
        "duration_display",
        "created_at",
        "completed_at"
    ],

    # Auto-generated display methods
    display_fields=[
        BadgeField(name="channel", title="Channel", variant="info", icon=Icons.NOTIFICATIONS),
        BadgeField(
            name="status",
            title="Status",
            label_map={
                "pending": "warning",
                "success": "success",
                "failed": "danger",
                "timeout": "danger",
                "partial": "warning",
            },
        ),
        UserField(name="user", title="User", header=True),
        DateTimeField(name="created_at", title="Created", ordering="created_at"),
        DateTimeField(name="completed_at", title="Completed", ordering="completed_at"),
    ],
    # Filters
    list_filter=["status", "wait_for_ack", "channel", "created_at"],
    search_fields=[
        "message_id",
        "channel",
        "user__username",
        "user__email",
        "error_message",
    ],
    # Autocomplete for user field
    autocomplete_fields=["user"],
    # Readonly fields
    readonly_fields=[
        "id",
        "message_id",
        "created_at",
        "completed_at",
        "data_display",
        "error_details_display",
        "delivery_stats_display",
    ],
    # Date hierarchy
    date_hierarchy="created_at",
    # Per page
    list_per_page=50,
)


__all__ = ["centrifugolog_config"]
