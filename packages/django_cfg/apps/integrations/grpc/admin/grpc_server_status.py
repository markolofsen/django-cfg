"""
gRPC Server Status Admin.

PydanticAdmin for GRPCServerStatus model with server monitoring and lifecycle tracking.
"""

from django.contrib import admin
from django_cfg.modules.django_admin import Icons, computed_field
from django_cfg.modules.django_admin.base import PydanticAdmin

from ..models import GRPCServerStatus
from .config import grpcserverstatus_config


@admin.register(GRPCServerStatus)
class GRPCServerStatusAdmin(PydanticAdmin):
    """
    Admin interface for gRPC server status monitoring.

    Features:
    - Real-time server status indicators
    - Uptime tracking and display
    - Process information (PID, hostname)
    - Service registration details
    - Error tracking and display
    """

    config = grpcserverstatus_config

    @computed_field("Uptime", ordering="started_at")
    def uptime_display(self, obj):
        """Display server uptime with performance indicator."""
        uptime_text = obj.uptime_display

        if not obj.is_running:
            return self.html.badge(
                uptime_text,
                variant="secondary",
                icon=Icons.SCHEDULE
            )

        # Color code based on uptime
        uptime_seconds = obj.uptime_seconds
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
            self.html.key_value(
                "Max Workers",
                self.html.badge(str(obj.max_workers), variant="secondary", icon=Icons.SETTINGS)
            ),
            self.html.key_value(
                "Reflection",
                self.html.badge(
                    "Enabled" if obj.enable_reflection else "Disabled",
                    variant="success" if obj.enable_reflection else "secondary",
                    icon=Icons.VISIBILITY if obj.enable_reflection else Icons.VISIBILITY_OFF
                )
            ),
            self.html.key_value(
                "Health Check",
                self.html.badge(
                    "Enabled" if obj.enable_health_check else "Disabled",
                    variant="success" if obj.enable_health_check else "secondary",
                    icon=Icons.HEALTH_AND_SAFETY if obj.enable_health_check else Icons.CANCEL
                )
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

    def registered_services_display(self, obj):
        """Display registered services."""
        if not obj.registered_services:
            return self.html.empty("No services registered")

        import json
        try:
            formatted = json.dumps(obj.registered_services, indent=2)
            return self.html.code_block(formatted, language="json", max_height="400px")
        except Exception:
            return self.html.code(str(obj.registered_services))

    registered_services_display.short_description = "Registered Services"

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
                self.html.badge(obj.uptime_display, variant="primary", icon=Icons.TIMER)
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
                {"fields": ("server_config_display", "host", "port", "max_workers", "enable_reflection", "enable_health_check")},
            ),
            (
                "Process Information",
                {"fields": ("process_info_display", "pid", "hostname", "is_running")},
            ),
            (
                "Lifecycle",
                {"fields": ("lifecycle_display", "started_at", "last_heartbeat", "stopped_at", "uptime_display")},
            ),
        ]

        # Add registered services section if available
        if obj and obj.registered_services:
            fieldsets.append(
                (
                    "Registered Services",
                    {"fields": ("registered_services_display",), "classes": ("collapse",)},
                )
            )

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
