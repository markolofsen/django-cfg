"""
gRPC Request Log Admin.

PydanticAdmin for GRPCRequestLog model with custom computed fields.
"""

import json

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
    - Formatted JSON for request/response data
    - Error details with highlighted display
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

    def request_data_display(self, obj):
        """Display formatted JSON request data."""
        if not obj.request_data:
            return self.html.empty("No request data logged")

        try:
            formatted = json.dumps(obj.request_data, indent=2)
            return self.html.code_block(formatted, language="json", max_height="400px")
        except Exception:
            return str(obj.request_data)

    request_data_display.short_description = "Request Data"

    def response_data_display(self, obj):
        """Display formatted JSON response data."""
        if not obj.response_data:
            return self.html.empty("No response data logged")

        try:
            formatted = json.dumps(obj.response_data, indent=2)
            return self.html.code_block(formatted, language="json", max_height="400px")
        except Exception:
            return str(obj.response_data)

    response_data_display.short_description = "Response Data"

    def error_details_display(self, obj):
        """Display error information if request failed."""
        if obj.is_successful or obj.status == "pending":
            return self.html.inline(
                self.html.icon(Icons.CHECK_CIRCLE, size="sm"),
                self.html.text("No errors", variant="success"),
                separator=" "
            )

        # gRPC status code
        code_line = self.html.key_value(
            "gRPC Status",
            self.html.badge(obj.grpc_status_code, variant="danger", icon=Icons.ERROR)
        ) if obj.grpc_status_code else None

        # Error message
        msg_line = self.html.key_value(
            "Message",
            self.html.text(obj.error_message, variant="danger")
        ) if obj.error_message else None

        # Error details
        details_line = None
        if obj.error_details:
            try:
                formatted = json.dumps(obj.error_details, indent=2)
                details_line = self.html.key_value(
                    "Details",
                    self.html.code_block(formatted, language="json", max_height="200px")
                )
            except Exception:
                pass

        return self.html.breakdown(code_line, msg_line, details_line) if (code_line or msg_line) else self.html.empty()

    error_details_display.short_description = "Error Details"

    def performance_stats_display(self, obj):
        """Display performance statistics."""
        # Duration
        duration_line = self.html.key_value(
            "Duration",
            self.html.number(obj.duration_ms, suffix="ms") if obj.duration_ms else "N/A"
        )

        # Request size
        request_size_line = self.html.key_value(
            "Request Size",
            self.html.number(obj.request_size, suffix=" bytes") if obj.request_size else "N/A"
        )

        # Response size
        response_size_line = self.html.key_value(
            "Response Size",
            self.html.number(obj.response_size, suffix=" bytes") if obj.response_size else "N/A"
        )

        # Authentication
        auth_line = self.html.key_value(
            "Authenticated",
            self.html.badge("Yes" if obj.is_authenticated else "No",
                          variant="success" if obj.is_authenticated else "secondary")
        )

        return self.html.breakdown(duration_line, request_size_line, response_size_line, auth_line)

    performance_stats_display.short_description = "Performance Statistics"

    def client_info_display(self, obj):
        """Display client information."""
        # Client IP
        ip_line = self.html.key_value(
            "Client IP",
            obj.client_ip if obj.client_ip else "N/A"
        )

        # User Agent
        ua_line = self.html.key_value(
            "User Agent",
            obj.user_agent if obj.user_agent else "N/A"
        )

        # Peer
        peer_line = self.html.key_value(
            "Peer",
            self.html.text(obj.peer, variant="secondary") if obj.peer else "N/A"
        )

        return self.html.breakdown(ip_line, ua_line, peer_line)

    client_info_display.short_description = "Client Information"

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
                {"fields": ("user", "is_authenticated")},
            ),
            (
                "Performance",
                {"fields": ("performance_stats_display", "duration_ms", "created_at", "completed_at")},
            ),
            (
                "Client Information",
                {"fields": ("client_info_display", "client_ip", "user_agent", "peer"), "classes": ("collapse",)},
            ),
        ]

        # Add request/response data sections if available
        if obj and obj.request_data:
            fieldsets.insert(
                3,
                (
                    "Request Data",
                    {"fields": ("request_data_display",), "classes": ("collapse",)},
                ),
            )

        if obj and obj.response_data:
            fieldsets.insert(
                4,
                (
                    "Response Data",
                    {"fields": ("response_data_display",), "classes": ("collapse",)},
                ),
            )

        # Add error section only if failed
        if obj and not obj.is_successful and obj.status != "pending":
            fieldsets.insert(
                5,
                (
                    "Error Details",
                    {"fields": ("error_details_display", "grpc_status_code", "error_message", "error_details")},
                ),
            )

        return fieldsets


__all__ = ["GRPCRequestLogAdmin"]
