"""
Admin for FrontendEvent model.
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

from django_cfg.apps.system.monitor.models.event import FrontendEvent

event_admin_config = AdminConfig(
    model=FrontendEvent,

    list_display=[
        "event_type",
        "level",
        "message",
        "url",
        "browser",
        "device_type",
        "ip_address",
        "user",
        "project_name",
        "environment",
        "build_id",
        "created_at",
    ],

    display_fields=[
        BadgeField(
            name="event_type",
            title="Type",
            label_map={
                "ERROR": "danger",
                "WARNING": "warning",
                "JS_ERROR": "danger",
                "NETWORK_ERROR": "warning",
                "INFO": "info",
                "PAGE_VIEW": "secondary",
                "PERFORMANCE": "primary",
                "CONSOLE": "secondary",
            },
        ),
        BadgeField(
            name="level",
            title="Level",
            label_map={
                "error": "danger",
                "warn": "warning",
                "info": "info",
                "debug": "secondary",
            },
        ),
        TextField(name="message", title="Message", truncate=80),
        TextField(name="url", title="Page URL", truncate=60),
        TextField(name="browser", title="Browser"),
        TextField(name="device_type", title="Device"),
        TextField(name="ip_address", title="IP"),
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
        TextField(name="build_id", title="Build", truncate=12),
        DateTimeField(name="created_at", title="Time", show_relative=True),
    ],

    list_filter=["event_type", "level", "environment", "project_name", "device_type", "browser"],
    search_fields=["message", "url", "ip_address", "fingerprint", "http_url", "build_id"],
    ordering=["-created_at"],
    date_hierarchy="created_at",

    readonly_fields=[
        "event_type", "level", "message", "stack_trace", "url",
        "http_status", "http_method", "http_url",
        "user_agent", "ip_address", "device_type", "os", "browser",
        "fingerprint", "user", "anonymous_session", "extra",
        "project_name", "environment", "build_id", "created_at",
    ],

    fieldsets=[
        FieldsetConfig(
            title="Event",
            fields=["event_type", "level", "message", "stack_trace"],
        ),
        FieldsetConfig(
            title="Page",
            fields=["url", "project_name", "environment", "build_id"],
        ),
        FieldsetConfig(
            title="Network",
            fields=["http_status", "http_method", "http_url"],
        ),
        FieldsetConfig(
            title="Client",
            fields=["ip_address", "device_type", "os", "browser", "user_agent", "fingerprint"],
        ),
        FieldsetConfig(
            title="Session",
            fields=["user", "anonymous_session"],
        ),
        FieldsetConfig(
            title="Extra",
            fields=["extra"],
            collapsed=True,
        ),
        FieldsetConfig(
            title="Meta",
            fields=["created_at"],
        ),
    ],
)


@admin.register(FrontendEvent)
class FrontendEventAdmin(PydanticAdmin):
    config = event_admin_config
