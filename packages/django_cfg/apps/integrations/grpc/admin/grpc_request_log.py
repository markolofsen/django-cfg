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

    def request_data_display(self, obj):
        """Display formatted JSON request data."""
        if not obj.request_data:
            return self.html.empty("No request data logged")

        try:
            formatted = json.dumps(obj.request_data, indent=2)
            return self.html.code_block(formatted, language="json", max_height="400px")
        except Exception:
            return self.html.code(str(obj.request_data))

    request_data_display.short_description = "Request Data"

    def response_data_display(self, obj):
        """Display formatted JSON response data."""
        if not obj.response_data:
            return self.html.empty("No response data logged")

        try:
            formatted = json.dumps(obj.response_data, indent=2)
            return self.html.code_block(formatted, language="json", max_height="400px")
        except Exception:
            return self.html.code(str(obj.response_data))

    response_data_display.short_description = "Response Data"

    def error_details_display(self, obj):
        """Display error information if request failed."""
        if obj.is_successful or obj.status == "pending":
            return self.html.inline(
                self.html.icon(Icons.CHECK_CIRCLE, size="sm"),
                self.html.text("No errors", variant="success"),
                separator=" "
            )

        # Error details JSON
        error_details_json = None
        if obj.error_details:
            try:
                formatted = json.dumps(obj.error_details, indent=2)
                error_details_json = self.html.key_value(
                    "Details",
                    self.html.code_block(formatted, language="json", max_height="200px")
                )
            except Exception:
                pass

        return self.html.breakdown(
            self.html.key_value(
                "gRPC Status",
                self.html.badge(obj.grpc_status_code, variant="danger", icon=Icons.ERROR)
            ) if obj.grpc_status_code else None,
            self.html.key_value(
                "Message",
                self.html.text(obj.error_message, variant="danger")
            ) if obj.error_message else None,
            error_details_json,
        )

    error_details_display.short_description = "Error Details"

    def performance_stats_display(self, obj):
        """Display performance statistics and authentication info."""
        return self.html.breakdown(
            self.html.key_value(
                "Duration",
                self.html.badge(f"{obj.duration_ms}ms", variant="info", icon=Icons.TIMER)
            ) if obj.duration_ms is not None else None,
            self.html.key_value(
                "Request Size",
                self.html.text(f"{obj.request_size:,} bytes", variant="secondary")
            ) if obj.request_size else None,
            self.html.key_value(
                "Response Size",
                self.html.text(f"{obj.response_size:,} bytes", variant="secondary")
            ) if obj.response_size else None,
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
        )

    performance_stats_display.short_description = "Performance Statistics"

    def client_info_display(self, obj):
        """Display client information."""
        return self.html.breakdown(
            self.html.key_value(
                "Client IP",
                self.html.text(obj.client_ip, variant="info") if obj.client_ip else self.html.empty("N/A")
            ),
            self.html.key_value(
                "User Agent",
                self.html.code(obj.user_agent)
            ) if obj.user_agent else None,
            self.html.key_value(
                "Peer",
                self.html.text(obj.peer, variant="secondary")
            ) if obj.peer else None,
        )

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
                {"fields": ("user", "api_key", "is_authenticated")},
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
