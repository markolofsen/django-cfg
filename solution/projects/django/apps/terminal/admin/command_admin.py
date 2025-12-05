"""
Admin for CommandHistory model.
"""

from django.contrib import admin
from django.utils.html import format_html

from django_cfg.modules.django_admin import (
    AdminConfig,
    BadgeField,
    DateTimeField,
    FieldsetConfig,
    TextField,
    Icons,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from apps.terminal.models import CommandHistory


command_admin_config = AdminConfig(
    model=CommandHistory,

    # Performance optimization
    select_related=["session", "session__user"],

    # List display
    list_display=[
        "id",
        "session",
        "command",
        "status",
        "exit_code",
        "started_at",
        "finished_at",
        "created_at",
    ],

    # Display fields with UI widgets
    display_fields=[
        TextField(
            name="command",
            title="Command",
            truncate=50,
        ),
        BadgeField(
            name="status",
            title="Status",
            variant="info",
            icon=Icons.CODE,
        ),
        TextField(
            name="exit_code",
            title="Exit",
        ),
        DateTimeField(
            name="started_at",
            title="Started",
            show_relative=True,
        ),
        DateTimeField(
            name="finished_at",
            title="Finished",
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
    list_display_links=["id"],
    list_filter=["status", "created_at", "session"],
    search_fields=["command", "stdout", "stderr"],
    ordering=["-created_at"],

    # Readonly - command history is immutable
    readonly_fields=[
        "id",
        "session",
        "command",
        "working_directory",
        "status",
        "stdout",
        "stderr",
        "exit_code",
        "started_at",
        "finished_at",
        "bytes_in",
        "bytes_out",
        "created_at",
        "updated_at",
    ],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="Command",
            fields=["id", "session", "command", "working_directory"],
        ),
        FieldsetConfig(
            title="Execution",
            fields=["status", "exit_code", "started_at", "finished_at"],
        ),
        FieldsetConfig(
            title="Output",
            fields=["stdout", "stderr"],
            description="Standard output and error streams",
        ),
        FieldsetConfig(
            title="Statistics",
            fields=["bytes_in", "bytes_out"],
            collapsed=True,
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=["created_at", "updated_at"],
            collapsed=True,
        ),
    ],
)


@admin.register(CommandHistory)
class CommandHistoryAdmin(PydanticAdmin):
    """Enhanced admin for CommandHistory model."""

    config = command_admin_config

    def has_add_permission(self, request):
        """Disable adding commands manually."""
        return False

    def has_change_permission(self, request, obj=None):
        """Disable editing commands."""
        return False
