"""
Admin for ServerEvent model.
"""

from django.contrib import admin

from django_cfg.modules.django_admin import (
    AdminConfig,
    BadgeField,
    DateTimeField,
    FieldsetConfig,
    TextField,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from django_cfg.apps.system.monitor.models.server_event import ServerEvent


def _mark_resolved(modeladmin, request, queryset):
    from django.utils import timezone
    queryset.update(
        is_resolved=True,
        resolved_at=timezone.now(),
        resolved_by=request.user,
    )


_mark_resolved.short_description = "Mark selected as resolved"


def _mark_unresolved(modeladmin, request, queryset):
    queryset.update(
        is_resolved=False,
        resolved_at=None,
        resolved_by=None,
    )


_mark_unresolved.short_description = "Reopen selected"


server_event_admin_config = AdminConfig(
    model=ServerEvent,

    list_display=[
        "event_type",
        "level",
        "message",
        "occurrence_count",
        "module",
        "func_name",
        "project_name",
        "environment",
        "last_seen",
        "is_resolved",
    ],

    display_fields=[
        BadgeField(
            name="event_type",
            title="Type",
            label_map={
                "SERVER_ERROR": "danger",
                "UNHANDLED_EXCEPTION": "danger",
                "RQ_FAILURE": "warning",
                "OOM_KILL": "danger",
                "SLOW_QUERY": "warning",
                "LOG_ERROR": "info",
            },
        ),
        BadgeField(
            name="level",
            title="Level",
            label_map={
                "error": "danger",
                "warning": "warning",
                "info": "info",
                "debug": "secondary",
            },
        ),
        TextField(name="message", title="Message", truncate=80),
        TextField(name="module", title="Module", truncate=50),
        TextField(name="func_name", title="Function"),
        TextField(name="occurrence_count", title="×"),
        TextField(name="project_name", title="Project"),
        BadgeField(
            name="environment",
            title="Env",
            label_map={
                "production": "danger",
                "staging": "warning",
                "development": "info",
            },
        ),
        DateTimeField(name="last_seen", title="Last Seen", show_relative=True),
        DateTimeField(name="first_seen", title="First Seen", show_relative=True),
    ],

    list_filter=["event_type", "level", "is_resolved", "environment", "project_name"],
    search_fields=["message", "fingerprint", "func_name", "module", "url", "project_name"],
    ordering=["-last_seen"],
    date_hierarchy="last_seen",

    readonly_fields=[
        "fingerprint", "event_type", "level", "message", "stack_trace",
        "logger_name", "url", "http_method", "http_status",
        "func_name", "module", "lineno", "extra",
        "project_name", "environment",
        "occurrence_count", "first_seen", "last_seen",
        "resolved_at", "resolved_by",
    ],

    fieldsets=[
        FieldsetConfig(
            title="Event",
            fields=["event_type", "level", "message", "stack_trace"],
        ),
        FieldsetConfig(
            title="Source",
            fields=["module", "func_name", "lineno", "logger_name"],
        ),
        FieldsetConfig(
            title="Request",
            fields=["url", "http_method", "http_status"],
        ),
        FieldsetConfig(
            title="Deduplication",
            fields=["fingerprint", "occurrence_count", "first_seen", "last_seen"],
        ),
        FieldsetConfig(
            title="Resolution",
            fields=["is_resolved", "resolved_at", "resolved_by"],
        ),
        FieldsetConfig(
            title="Context",
            fields=["project_name", "environment"],
        ),
        FieldsetConfig(
            title="Extra",
            fields=["extra"],
            collapsed=True,
        ),
    ],
)


@admin.register(ServerEvent)
class ServerEventAdmin(PydanticAdmin):
    config = server_event_admin_config
    actions = [_mark_resolved, _mark_unresolved]
