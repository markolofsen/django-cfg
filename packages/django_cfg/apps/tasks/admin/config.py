"""
Admin configuration for Task models.

Declarative AdminConfig using PydanticAdmin patterns.
"""

from django_cfg.modules.django_admin import (
    AdminConfig,
    BadgeField,
    DateTimeField,
    Icons,
    UserField,
)

from ..models import TaskLog


# Declarative configuration for TaskLog
tasklog_config = AdminConfig(
    model=TaskLog,

    # Performance optimization
    select_related=["user"],

    # List display
    list_display=[
        "task_name",
        "queue_badge",
        "status_badge",
        "user",
        "duration_display",
        "retry_count",
        "created_at",
        "completed_at",
    ],

    # Auto-generated display methods
    display_fields=[
        BadgeField(
            name="queue_name",
            title="Queue",
            variant="info",
            icon=Icons.LAYERS,
        ),
        BadgeField(
            name="status",
            title="Status",
            label_map={
                "queued": "secondary",
                "in_progress": "info",
                "completed": "success",
                "failed": "danger",
                "canceled": "warning",
            },
        ),
        UserField(name="user", title="User", header=True),
        DateTimeField(name="created_at", title="Created", ordering="created_at"),
        DateTimeField(name="started_at", title="Started", ordering="started_at"),
        DateTimeField(name="completed_at", title="Completed", ordering="completed_at"),
    ],

    # Filters
    list_filter=["status", "task_name", "queue_name", "created_at"],
    search_fields=[
        "job_id",
        "task_name",
        "worker_id",
        "error_message",
        "user__username",
        "user__email",
    ],

    # Autocomplete for user field
    autocomplete_fields=["user"],

    # Readonly fields
    readonly_fields=[
        "id",
        "job_id",
        "created_at",
        "started_at",
        "completed_at",
        "duration_ms",
        "worker_id",
    ],

    # Date hierarchy
    date_hierarchy="created_at",

    # Per page
    list_per_page=50,

    # Ordering
    ordering=["-created_at"],
)


__all__ = ["tasklog_config"]
