"""
Admin configuration for Web Push models.

Declarative AdminConfig using PydanticAdmin patterns.
"""

from django_cfg.modules.django_admin import (
    AdminConfig,
    BadgeField,
    DateTimeField,
    Icons,
    UserField,
)

from ..models import PushSubscription


# Declarative configuration for PushSubscription
pushsubscription_config = AdminConfig(
    model=PushSubscription,
    # Performance optimization
    select_related=["user"],

    # List display
    list_display=[
        "user",
        "endpoint_short",
        "status_badge",
        "created_at",
    ],

    # Auto-generated display methods
    display_fields=[
        UserField(name="user", title="User", header=True),
        BadgeField(
            name="is_active",
            title="Status",
            label_map={
                True: "success",
                False: "danger",
            },
        ),
        DateTimeField(name="created_at", title="Created", ordering="created_at"),
        DateTimeField(name="updated_at", title="Updated", ordering="updated_at"),
    ],

    # Filters
    list_filter=["is_active", "created_at"],
    search_fields=[
        "user__username",
        "user__email",
        "endpoint",
    ],

    # Autocomplete for user field
    autocomplete_fields=["user"],

    # Readonly fields
    readonly_fields=[
        "id",
        "endpoint",
        "p256dh",
        "auth",
        "created_at",
        "updated_at",
    ],

    # Date hierarchy
    date_hierarchy="created_at",

    # Per page
    list_per_page=50,
)


__all__ = ["pushsubscription_config"]
