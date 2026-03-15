"""
GrpcAgentConnectionEvent model.

Immutable event log for state transitions.
Append-only for audit trail and timeline reconstruction.

Created: 2025-12-28
Refactored: 2025-12-29
"""

import uuid

from django.db import models

from ...managers.connection_state import GrpcAgentConnectionEventManager


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
        "grpc.GrpcAgentConnectionState",
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

    @property
    def is_error(self) -> bool:
        """Check if this is an error event."""
        return self.event_type == self.EventType.ERROR

    @property
    def is_connection(self) -> bool:
        """Check if this is a connection event."""
        return self.event_type == self.EventType.CONNECTED

    @property
    def is_disconnection(self) -> bool:
        """Check if this is a disconnection event."""
        return self.event_type == self.EventType.DISCONNECTED
