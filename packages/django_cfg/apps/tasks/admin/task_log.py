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
            return self.html.code_block(formatted, language="json", max_height="400px")
        except Exception:
            return str(data)

    args_display.short_description = "Task Arguments"

    def error_details_display(self, obj):
        """Display error information if task failed."""
        if obj.is_successful or obj.status in ["queued", "in_progress"]:
            return self.html.inline(
                self.html.icon(Icons.CHECK_CIRCLE, size="sm"),
                self.html.text("No errors", variant="success"),
                separator=" "
            )

        if not obj.error_message:
            return self.html.empty("No error message")

        return self.html.inline(
            self.html.icon(Icons.ERROR, size="sm"),
            self.html.code(obj.error_message, css_class="text-font-danger-light dark:text-font-danger-dark text-sm"),
            separator=" "
        )

    error_details_display.short_description = "Error Details"

    def retry_info_display(self, obj):
        """Display retry information."""
        if obj.retry_count == 0:
            return self.html.inline(
                self.html.icon(Icons.CHECK_CIRCLE, size="sm"),
                self.html.text("No retries", muted=True),
                separator=" "
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

        return self.html.badge(f"{obj.retry_count} retries", variant=variant, icon=icon)

    retry_info_display.short_description = "Retry Info"

    def performance_summary(self, obj):
        """Display performance summary."""
        # Duration
        duration_line = None
        if obj.duration_ms is not None:
            if obj.duration_ms < 1000:
                duration_str = f"{obj.duration_ms}ms"
            else:
                duration_str = f"{obj.duration_ms / 1000:.2f}s"
            duration_line = self.html.key_value("Duration", duration_str)

        # Retry count
        retry_line = None
        if obj.retry_count > 0:
            retry_line = self.html.key_value(
                "Retries",
                self.html.badge(str(obj.retry_count), variant="warning")
            )

        # Worker ID
        worker_line = None
        if obj.worker_id:
            worker_line = self.html.key_value("Worker", self.html.code(obj.worker_id, css_class="text-xs"))

        return self.html.breakdown(duration_line, retry_line, worker_line) if (duration_line or retry_line or worker_line) else self.html.empty()

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
