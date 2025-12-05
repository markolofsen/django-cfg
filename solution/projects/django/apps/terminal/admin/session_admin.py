"""
Admin for TerminalSession model.
"""

from django.contrib import admin

from django_cfg.modules.django_admin import (
    AdminConfig,
    BadgeField,
    DateTimeField,
    FieldsetConfig,
    TextField,
    UserField,
    Icons,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from apps.terminal.models import TerminalSession


# Badge color mapping for status
def get_status_variant(status: str) -> str:
    """Get badge variant based on status."""
    variants = {
        'pending': 'warning',
        'connected': 'success',
        'disconnected': 'secondary',
        'error': 'danger',
    }
    return variants.get(status, 'secondary')


session_admin_config = AdminConfig(
    model=TerminalSession,

    # Performance optimization
    select_related=["user"],

    # List display
    list_display=[
        "id",
        "user",
        "name",
        "status",
        "electron_hostname",
        "commands_count",
        "connected_at",
        "last_heartbeat_at",
        "created_at",
    ],

    # Display fields with UI widgets
    display_fields=[
        UserField(
            name="user",
            title="User",
            ordering="user__username",
            header=True,
        ),
        TextField(
            name="name",
            title="Session Name",
            truncate=30,
        ),
        BadgeField(
            name="status",
            title="Status",
            variant="primary",
            icon=Icons.TERMINAL,
        ),
        TextField(
            name="electron_hostname",
            title="Electron Host",
            truncate=30,
        ),
        DateTimeField(
            name="connected_at",
            title="Connected",
            show_relative=True,
        ),
        DateTimeField(
            name="last_heartbeat_at",
            title="Last Heartbeat",
            show_relative=True,
        ),
        DateTimeField(
            name="created_at",
            title="Created",
            ordering="created_at",
            show_relative=True,
        ),
    ],

    # List options
    list_display_links=["id", "user"],
    list_filter=["status", "created_at", "user"],
    search_fields=["user__username", "name", "electron_hostname"],
    ordering=["-created_at"],

    # Form options
    autocomplete_fields=["user"],
    readonly_fields=[
        "id",
        "commands_count",
        "bytes_sent",
        "bytes_received",
        "connected_at",
        "disconnected_at",
        "last_heartbeat_at",
        "created_at",
        "updated_at",
    ],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="Session Info",
            fields=["id", "user", "name", "status"],
        ),
        FieldsetConfig(
            title="Electron Client",
            fields=["electron_hostname", "electron_version"],
            description="Connected Electron application info",
        ),
        FieldsetConfig(
            title="Terminal Settings",
            fields=["working_directory", "shell", "environment"],
        ),
        FieldsetConfig(
            title="Statistics",
            fields=["commands_count", "bytes_sent", "bytes_received"],
            collapsed=True,
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=["connected_at", "last_heartbeat_at", "disconnected_at", "created_at", "updated_at"],
            collapsed=True,
        ),
    ],
)


@admin.register(TerminalSession)
class TerminalSessionAdmin(PydanticAdmin):
    """Enhanced admin for TerminalSession model."""

    config = session_admin_config
