"""
Centrifugo Log Admin.

PydanticAdmin for CentrifugoLog model with custom computed fields.
"""

import json

from django.contrib import admin
from django_cfg.modules.django_admin import Icons, computed_field
from django_cfg.modules.django_admin.base import PydanticAdmin

from ..models import CentrifugoLog
from .config import centrifugolog_config


@admin.register(CentrifugoLog)
class CentrifugoLogAdmin(PydanticAdmin):
    """
    Centrifugo log admin with analytics and filtering.

    Features:
    - Color-coded status badges
    - ACK tracking visualization
    - Duration display with performance indicators
    - Formatted JSON for message data
    - Error details with highlighted display
    """

    config = centrifugolog_config

    @computed_field("Type", ordering="wait_for_ack")
    def type_badge(self, obj):
        """Display badge showing if this publish waited for ACK."""
        if obj.wait_for_ack:
            return self.html.badge("ACK", variant="success", icon=Icons.CHECK_CIRCLE)
        else:
            return self.html.badge("FIRE", variant="secondary", icon=Icons.NOTIFICATIONS)

    @computed_field("ACKs", ordering="acks_received")
    def acks_display(self, obj):
        """Display ACK count with context."""
        if not obj.wait_for_ack:
            return self.html.empty()

        # If we have expected count
        if obj.acks_expected:
            rate = obj.delivery_rate
            if rate == 1.0:
                variant = "success"
                icon = Icons.CHECK_CIRCLE
            elif rate > 0:
                variant = "warning"
                icon = Icons.TIMER
            else:
                variant = "danger"
                icon = Icons.ERROR

            return self.html.badge(
                f"{obj.acks_received}/{obj.acks_expected}",
                variant=variant,
                icon=icon,
            )

        # Just show count
        if obj.acks_received > 0:
            return self.html.badge(
                f"{obj.acks_received} ACKs", variant="success", icon=Icons.CHECK_CIRCLE
            )
        else:
            return self.html.badge("0 ACKs", variant="danger", icon=Icons.ERROR)

    @computed_field("Duration", ordering="duration_ms")
    def duration_display(self, obj):
        """Display duration with color coding based on speed."""
        if obj.duration_ms is None:
            return self.html.empty()

        # Color code based on duration
        if obj.duration_ms < 100:
            variant = "success"  # Fast
            icon = Icons.SPEED
        elif obj.duration_ms < 500:
            variant = "warning"  # Moderate
            icon = Icons.TIMER
        else:
            variant = "danger"  # Slow
            icon = Icons.ERROR

        return self.html.badge(f"{obj.duration_ms}ms", variant=variant, icon=icon)

    def data_display(self, obj):
        """Display formatted JSON message data."""
        if not obj.data:
            return self.html.empty("No data")

        try:
            formatted = json.dumps(obj.data, indent=2)
            return self.html.code_block(formatted, language="json", max_height="400px")
        except Exception:
            return str(obj.data)

    data_display.short_description = "Message Data"

    def error_details_display(self, obj):
        """Display error information if publish failed."""
        if obj.is_successful or obj.status == "pending":
            return self.html.inline(
                self.html.icon(Icons.CHECK_CIRCLE, size="sm"),
                self.html.text("No errors", variant="success"),
                separator=" "
            )

        error_code_line = self.html.key_value(
            "Error Code",
            self.html.badge(obj.error_code, variant="danger", icon=Icons.ERROR)
        ) if obj.error_code else None

        error_msg_line = self.html.key_value(
            "Message",
            self.html.text(obj.error_message, variant="danger")
        ) if obj.error_message else None

        return self.html.breakdown(error_code_line, error_msg_line) if (error_code_line or error_msg_line) else self.html.empty()

    error_details_display.short_description = "Error Details"

    def delivery_stats_display(self, obj):
        """Display delivery statistics."""
        if not obj.wait_for_ack:
            return self.html.empty("No ACK tracking")

        # ACK timeout
        timeout_line = self.html.key_value(
            "Timeout",
            f"{obj.ack_timeout}s"
        ) if obj.ack_timeout else None

        # ACKs received
        received_line = self.html.key_value(
            "ACKs Received",
            self.html.badge(str(obj.acks_received), variant="info")
        )

        # ACKs expected (if known)
        expected_line = self.html.key_value(
            "ACKs Expected",
            str(obj.acks_expected)
        ) if obj.acks_expected else None

        # Delivery rate
        rate_line = None
        if obj.acks_expected and obj.delivery_rate is not None:
            rate_pct = obj.delivery_rate * 100
            rate_line = self.html.key_value(
                "Delivery Rate",
                self.html.number(rate_pct, precision=1, suffix="%")
            )

        return self.html.breakdown(timeout_line, received_line, expected_line, rate_line)

    delivery_stats_display.short_description = "Delivery Statistics"

    # Fieldsets for detail view
    def get_fieldsets(self, request, obj=None):
        """Dynamic fieldsets based on object state."""
        fieldsets = [
            (
                "Publish Information",
                {"fields": ("id", "message_id", "channel", "user", "status")},
            ),
            (
                "Message Data",
                {"fields": ("data_display",), "classes": ("collapse",)},
            ),
            ("Performance", {"fields": ("duration_ms", "created_at", "completed_at")}),
            ("Metadata", {"fields": ("caller_ip", "user_agent"), "classes": ("collapse",)}),
        ]

        # Add ACK tracking section if enabled
        if obj and obj.wait_for_ack:
            fieldsets.insert(
                2,
                (
                    "ACK Tracking",
                    {
                        "fields": (
                            "delivery_stats_display",
                            "wait_for_ack",
                            "ack_timeout",
                            "acks_received",
                            "acks_expected",
                        )
                    },
                ),
            )

        # Add error section only if failed
        if obj and not obj.is_successful and obj.status != "pending":
            fieldsets.insert(
                3,
                (
                    "Error Details",
                    {"fields": ("error_details_display", "error_code", "error_message")},
                ),
            )

        return fieldsets


__all__ = ["CentrifugoLogAdmin"]
