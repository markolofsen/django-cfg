"""
gRPC Server Status Admin.

PydanticAdmin for GRPCServerStatus model with server monitoring and lifecycle tracking.
"""

from django.contrib import admin
from django_cfg.modules.django_admin import Icons, computed_field
from django_cfg.modules.django_admin.base import PydanticAdmin

from ..models import GRPCServerStatus
from .config import grpcserverstatus_config


def format_uptime(seconds: int) -> str:
    """Format uptime in seconds to human readable string."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins}m {secs}s"
    elif seconds < 86400:
        hours = seconds // 3600
        mins = (seconds % 3600) // 60
        return f"{hours}h {mins}m"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}d {hours}h"


@admin.register(GRPCServerStatus)
class GRPCServerStatusAdmin(PydanticAdmin):
    """
    Admin interface for gRPC server status monitoring.

    Features:
    - Real-time server status indicators
    - Uptime tracking and display
    - Process information (PID, hostname)
    - Error tracking and display
    """

    config = grpcserverstatus_config

    @computed_field("Uptime", ordering="started_at")
    def uptime_display(self, obj):
        """Display server uptime with performance indicator."""
        uptime_seconds = obj.uptime_seconds
        uptime_text = format_uptime(uptime_seconds)

        if not obj.is_running:
            return self.html.badge(
                uptime_text,
                variant="secondary",
                icon=Icons.SCHEDULE
            )

        # Color code based on uptime
        if uptime_seconds > 86400:  # > 1 day
            variant = "success"
            icon = Icons.CHECK_CIRCLE
        elif uptime_seconds > 3600:  # > 1 hour
            variant = "info"
            icon = Icons.TIMER
        else:  # < 1 hour
            variant = "warning"
            icon = Icons.SCHEDULE

        return self.html.badge(uptime_text, variant=variant, icon=icon)

    def server_config_display(self, obj):
        """Display server configuration details."""
        return self.html.breakdown(
            self.html.key_value(
                "Address",
                self.html.badge(obj.address, variant="info", icon=Icons.CLOUD)
            ),
            self.html.key_value(
                "Host",
                self.html.code(obj.host)
            ),
            self.html.key_value(
                "Port",
                self.html.text(str(obj.port), variant="primary")
            ),
        )

    server_config_display.short_description = "Server Configuration"

    def process_info_display(self, obj):
        """Display process information."""
        return self.html.breakdown(
            self.html.key_value(
                "Instance ID",
                self.html.code(obj.instance_id)
            ),
            self.html.key_value(
                "PID",
                self.html.badge(str(obj.pid), variant="info", icon=Icons.MEMORY)
            ),
            self.html.key_value(
                "Hostname",
                self.html.text(obj.hostname, variant="secondary")
            ),
            self.html.key_value(
                "Running",
                self.html.badge(
                    "Yes" if obj.is_running else "No",
                    variant="success" if obj.is_running else "danger",
                    icon=Icons.CHECK_CIRCLE if obj.is_running else Icons.CANCEL
                )
            ),
        )

    process_info_display.short_description = "Process Information"

    def error_display(self, obj):
        """Display error information if status is ERROR."""
        if obj.status != "error" or not obj.error_message:
            return self.html.inline(
                self.html.icon(Icons.CHECK_CIRCLE, size="sm"),
                self.html.text("No errors", variant="success"),
                separator=" "
            )

        return self.html.breakdown(
            self.html.key_value(
                "Error Message",
                self.html.text(obj.error_message, variant="danger")
            ),
            self.html.key_value(
                "Stopped At",
                self.html.text(
                    obj.stopped_at.strftime("%Y-%m-%d %H:%M:%S") if obj.stopped_at else "N/A",
                    variant="secondary"
                )
            ),
        )

    error_display.short_description = "Error Details"

    def lifecycle_display(self, obj):
        """Display server lifecycle timestamps."""
        uptime_text = format_uptime(obj.uptime_seconds)
        return self.html.breakdown(
            self.html.key_value(
                "Started",
                self.html.text(
                    obj.started_at.strftime("%Y-%m-%d %H:%M:%S"),
                    variant="success"
                )
            ),
            self.html.key_value(
                "Last Heartbeat",
                self.html.text(
                    obj.last_heartbeat.strftime("%Y-%m-%d %H:%M:%S"),
                    variant="info"
                )
            ) if obj.last_heartbeat else None,
            self.html.key_value(
                "Stopped",
                self.html.text(
                    obj.stopped_at.strftime("%Y-%m-%d %H:%M:%S"),
                    variant="danger"
                )
            ) if obj.stopped_at else None,
            self.html.key_value(
                "Uptime",
                self.html.badge(uptime_text, variant="primary", icon=Icons.TIMER)
            ),
        )

    lifecycle_display.short_description = "Lifecycle"

    # Fieldsets for detail view
    def get_fieldsets(self, request, obj=None):
        """Dynamic fieldsets based on object state."""
        fieldsets = [
            (
                "Server Identity",
                {"fields": ("id", "instance_id", "address", "status")},
            ),
            (
                "Configuration",
                {"fields": ("server_config_display", "host", "port")},
            ),
            (
                "Process Information",
                {"fields": ("process_info_display", "pid", "hostname")},
            ),
            (
                "Lifecycle",
                {"fields": ("lifecycle_display", "started_at", "last_heartbeat", "stopped_at", "uptime_display")},
            ),
        ]

        # Add error section only if status is ERROR
        if obj and obj.status == "error":
            fieldsets.append(
                (
                    "Error Details",
                    {"fields": ("error_display", "error_message")},
                )
            )

        return fieldsets


__all__ = ["GRPCServerStatusAdmin"]
