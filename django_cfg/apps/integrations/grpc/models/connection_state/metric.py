"""
GrpcAgentConnectionMetric model.

Time-series metrics for connection quality.
Sampled at regular intervals for trend analysis and graph visualization.

Created: 2025-12-28
Refactored: 2025-12-29
"""

import uuid

from django.db import models

from ...managers.connection_state import GrpcAgentConnectionMetricManager


class GrpcAgentConnectionMetric(models.Model):
    """
    Time-series metrics for connection quality.

    Sampled at regular intervals for trend analysis and graph visualization.
    """

    class HealthStatus(models.TextChoices):
        HEALTHY = "healthy", "Healthy"
        DEGRADED = "degraded", "Degraded"
        POOR = "poor", "Poor"
        UNKNOWN = "unknown", "Unknown"

    # Identity
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    connection_state = models.ForeignKey(
        "grpc.GrpcAgentConnectionState",
        on_delete=models.CASCADE,
        related_name="metrics",
        help_text="Parent connection state",
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Metric sample time",
    )

    # Latency/RTT metrics
    rtt_min_ms = models.FloatField(
        null=True,
        blank=True,
        help_text="Minimum RTT in milliseconds",
    )
    rtt_max_ms = models.FloatField(
        null=True,
        blank=True,
        help_text="Maximum RTT in milliseconds",
    )
    rtt_mean_ms = models.FloatField(
        null=True,
        blank=True,
        help_text="Mean RTT in milliseconds",
    )
    rtt_stddev_ms = models.FloatField(
        null=True,
        blank=True,
        help_text="RTT standard deviation in milliseconds",
    )

    # Packet loss
    packet_loss_percent = models.FloatField(
        null=True,
        blank=True,
        help_text="Packet loss percentage",
    )
    packets_sent = models.IntegerField(
        null=True,
        blank=True,
        help_text="Total packets sent in sample window",
    )
    packets_received = models.IntegerField(
        null=True,
        blank=True,
        help_text="Total packets received in sample window",
    )

    # Keepalive metrics
    keepalive_sent = models.IntegerField(
        default=0,
        help_text="Keepalive pings sent",
    )
    keepalive_ack = models.IntegerField(
        default=0,
        help_text="Keepalive acknowledgments received",
    )
    keepalive_timeout = models.IntegerField(
        default=0,
        help_text="Keepalive timeouts",
    )

    # Stream health
    active_streams = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of active streams",
    )
    failed_streams = models.IntegerField(
        default=0,
        help_text="Number of failed streams in sample window",
    )

    # Health assessment
    health_status = models.CharField(
        max_length=20,
        choices=HealthStatus.choices,
        default=HealthStatus.UNKNOWN,
        db_index=True,
        help_text="Calculated health status",
    )
    sample_window_seconds = models.IntegerField(
        default=30,
        help_text="Duration of sample window in seconds",
    )

    # Custom manager
    objects: GrpcAgentConnectionMetricManager = GrpcAgentConnectionMetricManager()

    class Meta:
        verbose_name = "gRPC Agent Connection Metric"
        verbose_name_plural = "gRPC Agent Connection Metrics"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["connection_state", "-timestamp"]),
            models.Index(fields=["health_status", "-timestamp"]),
        ]

    def __str__(self) -> str:
        return f"{self.connection_state.machine_name}: {self.health_status} at {self.timestamp}"

    def calculate_health_status(self) -> str:
        """Calculate health status from metrics."""
        issues = 0

        # Check packet loss
        if self.packet_loss_percent and self.packet_loss_percent > 5:
            issues += 1

        # Check RTT
        if self.rtt_mean_ms and self.rtt_mean_ms > 1000:
            issues += 1

        # Check keepalive timeouts
        if self.keepalive_timeout > 0 and self.keepalive_sent > 0:
            timeout_rate = self.keepalive_timeout / self.keepalive_sent
            if timeout_rate > 0.1:  # >10% timeout rate
                issues += 1

        # Check failed streams
        if self.failed_streams > 0:
            issues += 1

        # Determine status
        if issues >= 3:
            return self.HealthStatus.POOR
        elif issues >= 1:
            return self.HealthStatus.DEGRADED
        return self.HealthStatus.HEALTHY

    def save(self, *args, **kwargs):
        """Auto-calculate health status before saving."""
        if not self.health_status or self.health_status == self.HealthStatus.UNKNOWN:
            self.health_status = self.calculate_health_status()
        super().save(*args, **kwargs)

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def is_healthy(self) -> bool:
        """Check if this metric indicates healthy connection."""
        return self.health_status == self.HealthStatus.HEALTHY

    @property
    def is_degraded(self) -> bool:
        """Check if this metric indicates degraded connection."""
        return self.health_status == self.HealthStatus.DEGRADED

    @property
    def is_poor(self) -> bool:
        """Check if this metric indicates poor connection."""
        return self.health_status == self.HealthStatus.POOR

    @property
    def keepalive_success_rate(self) -> float:
        """Calculate keepalive success rate (0.0 to 1.0)."""
        if not self.keepalive_sent:
            return 1.0
        return self.keepalive_ack / self.keepalive_sent
