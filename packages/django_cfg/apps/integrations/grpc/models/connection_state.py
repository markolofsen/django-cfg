"""
gRPC Agent Connection State Models.

Tracks connection state per machine (independent of sessions) for:
- Real-time dashboard visualization
- Network graph on frontend
- Connection quality monitoring
- Historical analysis

Created: 2025-12-28
Status: Production
"""

import uuid
from django.db import models
from django.utils import timezone


class GrpcAgentConnectionState(models.Model):
    """
    Current connection state per machine.

    One record per unique machine_id, updated on each connection event.
    Designed for fast dashboard queries with denormalized current metrics.
    """

    class ConnectionStatus(models.TextChoices):
        CONNECTED = "connected", "Connected"
        DISCONNECTED = "disconnected", "Disconnected"
        RECONNECTING = "reconnecting", "Reconnecting"
        ERROR = "error", "Error"
        UNKNOWN = "unknown", "Unknown"

    # Identity
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    machine_id = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="Unique machine identifier (e.g., hostname or UUID)",
    )
    machine_name = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Human-readable machine name",
    )

    # Connection state
    status = models.CharField(
        max_length=20,
        choices=ConnectionStatus.choices,
        default=ConnectionStatus.UNKNOWN,
        db_index=True,
        help_text="Current connection status",
    )

    # Network info
    last_known_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="Last known IP address",
    )
    client_version = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="Agent client version",
    )

    # Timestamps
    first_connected_at = models.DateTimeField(
        auto_now_add=True,
        help_text="First time this machine connected",
    )
    last_connected_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last successful connection time",
    )
    last_disconnected_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last disconnection time",
    )

    # Error tracking
    last_error_message = models.TextField(
        blank=True,
        default="",
        help_text="Last error message",
    )
    last_error_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last error timestamp",
    )
    consecutive_error_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of consecutive errors",
    )

    # Metrics snapshot (denormalized for fast dashboard queries)
    current_rtt_ms = models.FloatField(
        null=True,
        blank=True,
        help_text="Current round-trip time in milliseconds",
    )
    current_packet_loss_percent = models.FloatField(
        null=True,
        blank=True,
        help_text="Current packet loss percentage",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Custom manager
    from ..managers import GrpcAgentConnectionStateManager
    objects: GrpcAgentConnectionStateManager = GrpcAgentConnectionStateManager()

    class Meta:
        verbose_name = "gRPC Agent Connection State"
        verbose_name_plural = "gRPC Agent Connection States"
        ordering = ["-last_connected_at"]
        indexes = [
            models.Index(fields=["status", "-last_connected_at"]),
            models.Index(fields=["machine_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.machine_name} ({self.status})"

    def mark_connected(self, ip_address: str = None, client_version: str = None):
        """Mark machine as connected."""
        self.status = self.ConnectionStatus.CONNECTED
        self.last_connected_at = timezone.now()
        self.consecutive_error_count = 0
        if ip_address:
            self.last_known_ip = ip_address
        if client_version:
            self.client_version = client_version
        self.save(update_fields=[
            "status", "last_connected_at", "consecutive_error_count",
            "last_known_ip", "client_version", "updated_at",
        ])

    def mark_disconnected(self):
        """Mark machine as disconnected."""
        self.status = self.ConnectionStatus.DISCONNECTED
        self.last_disconnected_at = timezone.now()
        self.save(update_fields=["status", "last_disconnected_at", "updated_at"])

    def mark_error(self, error_message: str):
        """Mark machine as having an error."""
        self.status = self.ConnectionStatus.ERROR
        self.last_error_message = error_message
        self.last_error_at = timezone.now()
        self.consecutive_error_count += 1
        self.save(update_fields=[
            "status", "last_error_message", "last_error_at",
            "consecutive_error_count", "updated_at",
        ])

    def update_metrics(self, rtt_ms: float = None, packet_loss_percent: float = None):
        """Update current metrics snapshot."""
        update_fields = ["updated_at"]
        if rtt_ms is not None:
            self.current_rtt_ms = rtt_ms
            update_fields.append("current_rtt_ms")
        if packet_loss_percent is not None:
            self.current_packet_loss_percent = packet_loss_percent
            update_fields.append("current_packet_loss_percent")
        self.save(update_fields=update_fields)

    @property
    def is_healthy(self) -> bool:
        """Check if connection is healthy."""
        if self.status != self.ConnectionStatus.CONNECTED:
            return False
        if self.consecutive_error_count > 0:
            return False
        if self.current_rtt_ms and self.current_rtt_ms > 1000:
            return False
        if self.current_packet_loss_percent and self.current_packet_loss_percent > 5:
            return False
        return True

    @property
    def uptime_seconds(self) -> float:
        """Get current connection uptime in seconds."""
        if self.status != self.ConnectionStatus.CONNECTED:
            return 0.0
        if not self.last_connected_at:
            return 0.0
        delta = timezone.now() - self.last_connected_at
        return delta.total_seconds()


class GrpcAgentConnectionEvent(models.Model):
    """
    Immutable event log for state transitions.

    Append-only for audit trail and timeline reconstruction.
    """

    class EventType(models.TextChoices):
        CONNECTED = "connected", "Connected"
        DISCONNECTED = "disconnected", "Disconnected"
        RECONNECTING = "reconnecting", "Reconnecting"
        ERROR = "error", "Error"

    # Identity
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    connection_state = models.ForeignKey(
        GrpcAgentConnectionState,
        on_delete=models.CASCADE,
        related_name="events",
        help_text="Parent connection state",
    )

    # Event details
    event_type = models.CharField(
        max_length=20,
        choices=EventType.choices,
        db_index=True,
        help_text="Type of event",
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When event occurred",
    )

    # Context
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address at time of event",
    )
    client_version = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="Client version at time of event",
    )

    # Error details (for error events)
    error_message = models.TextField(
        blank=True,
        default="",
        help_text="Error message if event_type is error",
    )
    error_code = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="Error code (e.g., gRPC status code)",
    )
    error_details = models.JSONField(
        null=True,
        blank=True,
        help_text="Additional error details as JSON",
    )

    # Duration (for disconnection events)
    duration_seconds = models.IntegerField(
        null=True,
        blank=True,
        help_text="Connection duration before this disconnect (seconds)",
    )

    # Custom manager
    from ..managers import GrpcAgentConnectionEventManager
    objects: GrpcAgentConnectionEventManager = GrpcAgentConnectionEventManager()

    class Meta:
        verbose_name = "gRPC Agent Connection Event"
        verbose_name_plural = "gRPC Agent Connection Events"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["connection_state", "-timestamp"]),
            models.Index(fields=["event_type", "-timestamp"]),
        ]

    def __str__(self) -> str:
        return f"{self.connection_state.machine_name}: {self.event_type} at {self.timestamp}"


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
        GrpcAgentConnectionState,
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
    from ..managers import GrpcAgentConnectionMetricManager
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
