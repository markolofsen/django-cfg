"""
GrpcAgentConnectionState model.

Tracks current connection state per machine for:
- Real-time dashboard visualization
- Network graph on frontend
- Connection quality monitoring

Created: 2025-12-28
Refactored: 2025-12-29
"""

import uuid

from django.db import models
from django.utils import timezone

from ...managers.connection_state import GrpcAgentConnectionStateManager


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

    # =========================================================================
    # Sync methods (no locking, for simple use cases)
    # =========================================================================

    def mark_connected(self, ip_address: str = None, client_version: str = None):
        """
        Mark machine as connected (SYNC, no locking).

        WARNING: For concurrent access, use amark_connected_safe()
        """
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
        """
        Mark machine as disconnected (SYNC, no locking).

        WARNING: For concurrent access, use amark_disconnected_safe()
        """
        self.status = self.ConnectionStatus.DISCONNECTED
        self.last_disconnected_at = timezone.now()
        self.save(update_fields=["status", "last_disconnected_at", "updated_at"])

    def mark_error(self, error_message: str):
        """
        Mark machine as having an error (SYNC, no locking).

        WARNING: For concurrent access, use amark_error_safe()
        """
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

    # =========================================================================
    # Async methods (delegate to manager for proper locking)
    # =========================================================================

    async def amark_connected_safe(
        self,
        ip_address: str = None,
        client_version: str = None,
    ) -> bool:
        """
        Mark machine as connected with row-level locking (ASYNC).

        Delegates to manager for proper transaction handling.

        Returns:
            True if status was updated, False if not found
        """
        result = await type(self).objects.amark_connected_safe(
            pk=self.pk,
            ip_address=ip_address,
            client_version=client_version,
        )
        if result:
            await self.arefresh_from_db()
        return result is not None

    async def amark_disconnected_safe(self) -> bool:
        """
        Mark machine as disconnected with row-level locking (ASYNC).

        Returns:
            True if status was updated, False if not found
        """
        result = await type(self).objects.amark_disconnected_safe(pk=self.pk)
        if result:
            await self.arefresh_from_db()
        return result is not None

    async def amark_error_safe(self, error_message: str) -> bool:
        """
        Mark machine as having an error with row-level locking (ASYNC).

        Returns:
            True if status was updated, False if not found
        """
        result = await type(self).objects.amark_error_safe(
            pk=self.pk,
            error_message=error_message,
        )
        if result:
            await self.arefresh_from_db()
        return result is not None

    # =========================================================================
    # Properties
    # =========================================================================

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
