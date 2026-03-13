"""
Admin for AnonymousSession model.
"""

from django.contrib import admin

from django_cfg.modules.django_admin import (
    AdminConfig,
    BadgeField,
    DateTimeField,
    FieldsetConfig,
    ShortUUIDField,
    TextField,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from django_cfg.apps.system.frontend_monitor.models.session import AnonymousSession

session_admin_config = AdminConfig(
    model=AnonymousSession,

    list_display=[
        "session_id",
        "ip_address",
        "user",
        "fingerprint",
        "matched_status",
        "first_seen",
        "last_seen",
    ],

    display_fields=[
        ShortUUIDField(name="session_id", title="Session ID"),
        TextField(name="ip_address", title="IP"),
        TextField(name="fingerprint", title="Fingerprint", truncate=20),
        BadgeField(
            name="matched_status",
            title="Status",
            label_map={
                "Matched": "success",
                "Anonymous": "secondary",
            },
        ),
        DateTimeField(name="first_seen", title="First Seen", show_relative=True),
        DateTimeField(name="last_seen", title="Last Seen", show_relative=True),
        DateTimeField(name="matched_at", title="Matched At", show_relative=True),
    ],

    list_filter=["fingerprint"],
    search_fields=["ip_address", "user_agent", "fingerprint"],
    ordering=["-last_seen"],

    readonly_fields=[
        "session_id", "ip_address", "user_agent", "fingerprint",
        "user", "first_seen", "last_seen", "matched_at",
    ],

    fieldsets=[
        FieldsetConfig(
            title="Session",
            fields=["session_id", "ip_address", "fingerprint"],
        ),
        FieldsetConfig(
            title="User Agent",
            fields=["user_agent"],
        ),
        FieldsetConfig(
            title="Authentication",
            fields=["user", "matched_at"],
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=["first_seen", "last_seen"],
        ),
    ],
)


@admin.register(AnonymousSession)
class AnonymousSessionAdmin(PydanticAdmin):
    config = session_admin_config

    def matched_status(self, obj):
        return "Matched" if obj.user_id else "Anonymous"

    matched_status.short_description = "Status"
