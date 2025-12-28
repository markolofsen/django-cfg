"""
gRPC Agent Connection State Admin.

PydanticAdmin for connection state, events, and metrics models.
"""

from django.contrib import admin
from django_cfg.modules.django_admin import Icons, computed_field
from django_cfg.modules.django_admin.base import PydanticAdmin

from ..models import (
    GrpcAgentConnectionState,
    GrpcAgentConnectionEvent,
    GrpcAgentConnectionMetric,
)
from .config import (
    grpcagentconnectionstate_config,
    grpcagentconnectionevent_config,
    grpcagentconnectionmetric_config,
)


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable string."""
    if seconds is None:
        return "N/A"
    seconds = int(seconds)
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


@admin.register(GrpcAgentConnectionState)
class GrpcAgentConnectionStateAdmin(PydanticAdmin):
    """
    Admin interface for gRPC agent connection state.

    Features:
    - Real-time connection status indicators
    - RTT and packet loss metrics
    - Error tracking
    - Uptime calculation
    """

    config = grpcagentconnectionstate_config

    @computed_field("Uptime", ordering="last_connected_at")
    def uptime_display(self, obj):
        """Display current uptime for connected machines."""
        uptime_seconds = obj.uptime_seconds
        uptime_text = format_duration(uptime_seconds)

        if obj.status != "connected":
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

    @computed_field("Health", ordering="current_rtt_ms")
    def health_indicator(self, obj):
        """Display health indicator based on metrics."""
        if obj.is_healthy:
            return self.html.badge("Healthy", variant="success", icon=Icons.CHECK_CIRCLE)
        elif obj.status == "connected":
            return self.html.badge("Degraded", variant="warning", icon=Icons.WARNING)
        else:
            return self.html.badge("Offline", variant="secondary", icon=Icons.CANCEL)

    def metrics_display(self, obj):
        """Display current metrics."""
        items = []

        if obj.current_rtt_ms is not None:
            rtt_variant = "success" if obj.current_rtt_ms < 100 else "warning" if obj.current_rtt_ms < 500 else "danger"
            items.append(
                self.html.key_value(
                    "RTT",
                    self.html.badge(f"{obj.current_rtt_ms:.1f}ms", variant=rtt_variant)
                )
            )

        if obj.current_packet_loss_percent is not None:
            loss_variant = "success" if obj.current_packet_loss_percent < 1 else "warning" if obj.current_packet_loss_percent < 5 else "danger"
            items.append(
                self.html.key_value(
                    "Packet Loss",
                    self.html.badge(f"{obj.current_packet_loss_percent:.1f}%", variant=loss_variant)
                )
            )

        if not items:
            return self.html.text("No metrics", variant="secondary")

        return self.html.breakdown(*items)

    metrics_display.short_description = "Current Metrics"

    def error_summary_display(self, obj):
        """Display error summary."""
        if obj.consecutive_error_count == 0 and not obj.last_error_message:
            return self.html.inline(
                self.html.icon(Icons.CHECK_CIRCLE, size="sm"),
                self.html.text("No errors", variant="success"),
                separator=" "
            )

        items = [
            self.html.key_value(
                "Consecutive Errors",
                self.html.badge(
                    str(obj.consecutive_error_count),
                    variant="danger" if obj.consecutive_error_count > 0 else "success"
                )
            )
        ]

        if obj.last_error_message:
            items.append(
                self.html.key_value(
                    "Last Error",
                    self.html.text(obj.last_error_message[:100], variant="danger")
                )
            )

        if obj.last_error_at:
            items.append(
                self.html.key_value(
                    "Error At",
                    self.html.text(
                        obj.last_error_at.strftime("%Y-%m-%d %H:%M:%S"),
                        variant="secondary"
                    )
                )
            )

        return self.html.breakdown(*items)

    error_summary_display.short_description = "Error Summary"


@admin.register(GrpcAgentConnectionEvent)
class GrpcAgentConnectionEventAdmin(PydanticAdmin):
    """
    Admin interface for gRPC agent connection events.

    Features:
    - Event timeline with type badges
    - Error details display
    - Duration tracking for disconnections
    """

    config = grpcagentconnectionevent_config

    def error_message_short(self, obj):
        """Display truncated error message."""
        if not obj.error_message:
            return "-"
        msg = obj.error_message[:50]
        if len(obj.error_message) > 50:
            msg += "..."
        return self.html.text(msg, variant="danger" if obj.event_type == "error" else "secondary")

    error_message_short.short_description = "Error"

    def duration_display(self, obj):
        """Display formatted duration."""
        if obj.duration_seconds is None:
            return "-"
        return self.html.badge(
            format_duration(obj.duration_seconds),
            variant="info",
            icon=Icons.TIMER
        )

    duration_display.short_description = "Duration"


@admin.register(GrpcAgentConnectionMetric)
class GrpcAgentConnectionMetricAdmin(PydanticAdmin):
    """
    Admin interface for gRPC agent connection metrics.

    Features:
    - Health status badges
    - RTT statistics display
    - Keepalive and stream metrics
    """

    config = grpcagentconnectionmetric_config

    def rtt_summary_display(self, obj):
        """Display RTT statistics summary."""
        if obj.rtt_mean_ms is None:
            return self.html.text("No data", variant="secondary")

        return self.html.breakdown(
            self.html.key_value("Min", self.html.text(f"{obj.rtt_min_ms or 0:.1f}ms")),
            self.html.key_value("Mean", self.html.badge(f"{obj.rtt_mean_ms:.1f}ms", variant="info")),
            self.html.key_value("Max", self.html.text(f"{obj.rtt_max_ms or 0:.1f}ms")),
            self.html.key_value("StdDev", self.html.text(f"{obj.rtt_stddev_ms or 0:.1f}ms")),
        )

    rtt_summary_display.short_description = "RTT Statistics"

    def keepalive_summary_display(self, obj):
        """Display keepalive statistics."""
        timeout_rate = 0
        if obj.keepalive_sent > 0:
            timeout_rate = (obj.keepalive_timeout / obj.keepalive_sent) * 100

        timeout_variant = "success" if timeout_rate < 5 else "warning" if timeout_rate < 20 else "danger"

        return self.html.breakdown(
            self.html.key_value("Sent", self.html.text(str(obj.keepalive_sent))),
            self.html.key_value("ACK", self.html.text(str(obj.keepalive_ack))),
            self.html.key_value(
                "Timeout",
                self.html.badge(
                    f"{obj.keepalive_timeout} ({timeout_rate:.1f}%)",
                    variant=timeout_variant
                )
            ),
        )

    keepalive_summary_display.short_description = "Keepalive Stats"


__all__ = [
    "GrpcAgentConnectionStateAdmin",
    "GrpcAgentConnectionEventAdmin",
    "GrpcAgentConnectionMetricAdmin",
]
