"""
gRPC Request Log Admin.

PydanticAdmin for GRPCRequestLog model with custom computed fields.
"""

from django.contrib import admin
from django_cfg.modules.django_admin import Icons, computed_field
from django_cfg.modules.django_admin.base import PydanticAdmin

from ..models import GRPCRequestLog
from .config import grpcrequestlog_config


@admin.register(GRPCRequestLog)
class GRPCRequestLogAdmin(PydanticAdmin):
    """
    gRPC request log admin with analytics and filtering.

    Features:
    - Color-coded status badges
    - Performance metrics visualization
    - Duration display with performance indicators
    """

    config = grpcrequestlog_config

    @computed_field("Service", ordering="service_name")
    def service_badge(self, obj):
        """Display service name as badge."""
        return self.html.badge(obj.service_name, variant="info", icon=Icons.API)

    @computed_field("Method", ordering="method_name")
    def method_badge(self, obj):
        """Display method name as badge."""
        return self.html.badge(obj.method_name, variant="secondary", icon=Icons.CODE)

    @computed_field("gRPC Status", ordering="grpc_status_code")
    def grpc_status_code_display(self, obj):
        """Display gRPC status code with color coding."""
        if not obj.grpc_status_code:
            return self.html.empty()

        # Color code based on status
        if obj.grpc_status_code == "OK":
            variant = "success"
            icon = Icons.CHECK_CIRCLE
        elif obj.grpc_status_code in ["CANCELLED", "DEADLINE_EXCEEDED"]:
            variant = "warning"
            icon = Icons.TIMER
        else:
            variant = "danger"
            icon = Icons.ERROR

        return self.html.badge(obj.grpc_status_code, variant=variant, icon=icon)

    @computed_field("API Key", ordering="api_key__name")
    def api_key_display(self, obj):
        """Display API key name if used for authentication."""
        if not obj.api_key:
            return self.html.empty()

        return self.html.badge(
            obj.api_key.name,
            variant="info" if obj.api_key.is_valid else "danger",
            icon=Icons.KEY
        )

    @computed_field("Duration", ordering="duration_ms")
    def duration_display(self, obj):
        """Display duration with color coding based on speed."""
        if obj.duration_ms is None:
            return self.html.empty()

        # Color code based on duration
        if obj.duration_ms < 100:
            variant = "success"  # Fast
            icon = Icons.SPEED
        elif obj.duration_ms < 1000:
            variant = "warning"  # Moderate
            icon = Icons.TIMER
        else:
            variant = "danger"  # Slow
            icon = Icons.ERROR

        return self.html.badge(f"{obj.duration_ms}ms", variant=variant, icon=icon)

    def performance_stats_display(self, obj):
        """Display performance statistics and authentication info."""
        return self.html.breakdown(
            self.html.key_value(
                "Duration",
                self.html.badge(f"{obj.duration_ms}ms", variant="info", icon=Icons.TIMER)
            ) if obj.duration_ms is not None else None,
            self.html.key_value(
                "Authenticated",
                self.html.badge(
                    "Yes" if obj.is_authenticated else "No",
                    variant="success" if obj.is_authenticated else "secondary",
                    icon=Icons.VERIFIED_USER if obj.is_authenticated else Icons.PERSON
                )
            ),
            self.html.key_value(
                "API Key",
                self.html.inline(
                    self.html.badge(obj.api_key.name, variant="info", icon=Icons.KEY),
                    self.html.text(f"({obj.api_key.masked_key})", variant="secondary"),
                    separator=" "
                )
            ) if obj.api_key else None,
            self.html.key_value(
                "Client IP",
                self.html.text(obj.client_ip, variant="info") if obj.client_ip else self.html.empty("N/A")
            ),
        )

    performance_stats_display.short_description = "Performance Statistics"

    def error_display(self, obj):
        """Display error information if request failed."""
        if obj.is_successful:
            return self.html.inline(
                self.html.icon(Icons.CHECK_CIRCLE, size="sm"),
                self.html.text("No errors", variant="success"),
                separator=" "
            )

        return self.html.breakdown(
            self.html.key_value(
                "gRPC Status",
                self.html.badge(obj.grpc_status_code, variant="danger", icon=Icons.ERROR)
            ) if obj.grpc_status_code else None,
            self.html.key_value(
                "Message",
                self.html.text(obj.error_message, variant="danger")
            ) if obj.error_message else None,
        )

    error_display.short_description = "Error Details"

    # Fieldsets for detail view
    def get_fieldsets(self, request, obj=None):
        """Dynamic fieldsets based on object state."""
        fieldsets = [
            (
                "Request Information",
                {"fields": ("id", "request_id", "full_method", "service_name", "method_name", "status")},
            ),
            (
                "User Context",
                {"fields": ("user", "api_key", "is_authenticated")},
            ),
            (
                "Performance",
                {"fields": ("performance_stats_display", "duration_ms", "client_ip", "created_at", "completed_at")},
            ),
        ]

        # Add error section only if failed
        if obj and not obj.is_successful:
            fieldsets.append(
                (
                    "Error Details",
                    {"fields": ("error_display", "grpc_status_code", "error_message")},
                )
            )

        return fieldsets


__all__ = ["GRPCRequestLogAdmin"]
