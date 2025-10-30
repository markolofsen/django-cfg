"""
Task Log Admin.

PydanticAdmin for TaskLog model with custom computed fields.
"""

import json

from django.contrib import admin
from django_cfg.modules.django_admin import Icons, computed_field
from django_cfg.modules.django_admin.base import PydanticAdmin

from ..models import TaskLog
from .config import tasklog_config


@admin.register(TaskLog)
class TaskLogAdmin(PydanticAdmin):
    """
    Task log admin with analytics and filtering.

    Features:
    - Color-coded status badges
    - Duration display with performance indicators
    - Retry count tracking
    - Formatted JSON for arguments
    - Error details with highlighted display
    """

    config = tasklog_config

    @computed_field("Queue", ordering="queue_name")
    def queue_badge(self, obj):
        """Display queue name as badge."""
        variant_map = {
            "critical": "danger",
            "high": "warning",
            "default": "primary",
            "low": "secondary",
            "background": "secondary",
        }
        variant = variant_map.get(obj.queue_name, "info")
        return self.html.badge(obj.queue_name, variant=variant, icon=Icons.LAYERS)

    @computed_field("Status", ordering="status")
    def status_badge(self, obj):
        """Display status with appropriate badge."""
        variant_map = {
            "queued": "secondary",
            "in_progress": "info",
            "completed": "success",
            "failed": "danger",
            "canceled": "warning",
        }
        icon_map = {
            "queued": Icons.TIMER,
            "in_progress": Icons.SPEED,
            "completed": Icons.CHECK_CIRCLE,
            "failed": Icons.ERROR,
            "canceled": Icons.WARNING,
        }
        variant = variant_map.get(obj.status, "secondary")
        icon = icon_map.get(obj.status, Icons.NOTIFICATIONS)
        return self.html.badge(obj.get_status_display(), variant=variant, icon=icon)

    @computed_field("Duration", ordering="duration_ms")
    def duration_display(self, obj):
        """Display duration with color coding based on speed."""
        if obj.duration_ms is None:
            return self.html.empty()

        # Color code based on duration
        if obj.duration_ms < 1000:  # < 1s
            variant = "success"  # Fast
            icon = Icons.SPEED
        elif obj.duration_ms < 5000:  # < 5s
            variant = "info"  # Normal
            icon = Icons.TIMER
        elif obj.duration_ms < 30000:  # < 30s
            variant = "warning"  # Slow
            icon = Icons.TIMER
        else:
            variant = "danger"  # Very slow
            icon = Icons.ERROR

        # Format duration
        if obj.duration_ms < 1000:
            duration_str = f"{obj.duration_ms}ms"
        else:
            duration_str = f"{obj.duration_ms / 1000:.2f}s"

        return self.html.badge(duration_str, variant=variant, icon=icon)

    def args_display(self, obj):
        """Display formatted JSON arguments."""
        if not obj.args and not obj.kwargs:
            return self.html.empty("No arguments")

        try:
            data = {}
            if obj.args:
                data["args"] = obj.args
            if obj.kwargs:
                data["kwargs"] = obj.kwargs

            formatted = json.dumps(data, indent=2)
            return f'<pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; max-height: 400px; overflow: auto; font-size: 12px; line-height: 1.5;">{formatted}</pre>'
        except Exception:
            return str(data)

    args_display.short_description = "Task Arguments"

    def error_details_display(self, obj):
        """Display error information if task failed."""
        if obj.is_successful or obj.status in ["queued", "in_progress"]:
            return self.html.inline(
                [
                    self.html.icon(Icons.CHECK_CIRCLE, size="sm"),
                    self.html.span("No errors", "text-green-600"),
                ]
            )

        if not obj.error_message:
            return self.html.empty("No error message")

        return self.html.inline(
            [
                self.html.icon(Icons.ERROR, size="sm"),
                self.html.span(obj.error_message, "text-red-600 font-mono text-sm"),
            ]
        )

    error_details_display.short_description = "Error Details"

    def retry_info_display(self, obj):
        """Display retry information."""
        if obj.retry_count == 0:
            return self.html.inline(
                [
                    self.html.icon(Icons.CHECK_CIRCLE, size="sm"),
                    self.html.span("No retries", "text-gray-600"),
                ]
            )

        # Show retry count with warning if high
        if obj.retry_count >= 3:
            variant = "danger"
            icon = Icons.ERROR
        elif obj.retry_count >= 2:
            variant = "warning"
            icon = Icons.WARNING
        else:
            variant = "info"
            icon = Icons.TIMER

        return self.html.inline(
            [
                self.html.badge(f"{obj.retry_count} retries", variant=variant, icon=icon),
            ]
        )

    retry_info_display.short_description = "Retry Info"

    def performance_summary(self, obj):
        """Display performance summary."""
        stats = []

        # Duration
        if obj.duration_ms is not None:
            if obj.duration_ms < 1000:
                duration_str = f"{obj.duration_ms}ms"
            else:
                duration_str = f"{obj.duration_ms / 1000:.2f}s"
            stats.append(
                self.html.inline(
                    [
                        self.html.span("Duration:", "font-semibold"),
                        self.html.span(duration_str, "text-gray-600"),
                    ],
                    separator=" ",
                )
            )

        # Retry count
        if obj.retry_count > 0:
            stats.append(
                self.html.inline(
                    [
                        self.html.span("Retries:", "font-semibold"),
                        self.html.badge(str(obj.retry_count), variant="warning"),
                    ],
                    separator=" ",
                )
            )

        # Worker ID
        if obj.worker_id:
            stats.append(
                self.html.inline(
                    [
                        self.html.span("Worker:", "font-semibold"),
                        self.html.span(obj.worker_id, "text-gray-600 font-mono text-xs"),
                    ],
                    separator=" ",
                )
            )

        return "<br>".join(stats) if stats else self.html.empty()

    performance_summary.short_description = "Performance"

    # Fieldsets for detail view
    def get_fieldsets(self, request, obj=None):
        """Dynamic fieldsets based on object state."""
        fieldsets = [
            (
                "Task Information",
                {
                    "fields": (
                        "id",
                        "job_id",
                        "task_name",
                        "queue_name",
                        "status",
                        "user",
                    )
                },
            ),
            (
                "Arguments",
                {"fields": ("args_display",), "classes": ("collapse",)},
            ),
            (
                "Performance",
                {
                    "fields": (
                        "performance_summary",
                        "created_at",
                        "started_at",
                        "completed_at",
                    )
                },
            ),
        ]

        # Add error section only if failed
        if obj and obj.is_failed:
            fieldsets.insert(
                2,
                (
                    "Error Details",
                    {
                        "fields": (
                            "error_details_display",
                            "error_message",
                            "retry_info_display",
                        )
                    },
                ),
            )

        return fieldsets


__all__ = ["TaskLogAdmin"]
