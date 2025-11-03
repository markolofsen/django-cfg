"""
Centrifugo Log Model.

Django model for tracking Centrifugo publish operations.
Mirrors legacy WebSocket solution RPCLog patterns for easy migration.
"""

from django.conf import settings
from django.db import models
from django.utils import timezone


class CentrifugoLog(models.Model):
    """
    Log of Centrifugo publish operations.

    Tracks all publish calls with ACK tracking, mirroring RPCLog functionality.
    Provides observability for debugging and monitoring.

    Fields mirror RPCLog for migration compatibility:
    - correlation_id → message_id
    - method → channel
    - params → data
    - status → status
    - duration_ms → duration_ms
    - is_event → is_notification

    Example:
        >>> log = CentrifugoLog.objects.create(
        ...     message_id="abc123",
        ...     channel="user#456",
        ...     data={"title": "Hello", "message": "World"},
        ...     wait_for_ack=True
        ... )
        >>> log.mark_success(acks_received=1, duration_ms=125)
    """

    # Custom manager
    from ..managers.centrifugo_log import CentrifugoLogManager

    objects: CentrifugoLogManager = CentrifugoLogManager()

    class StatusChoices(models.TextChoices):
        """Status of publish operation."""

        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        TIMEOUT = "timeout", "Timeout"
        PARTIAL = "partial", "Partial Delivery"  # Some ACKs received, not all

    # Identity
    message_id = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Unique message identifier (UUID)",
    )

    # Publish details
    channel = models.CharField(
        max_length=200,
        db_index=True,
        help_text="Centrifugo channel (e.g., user#123, broadcast)",
    )

    data = models.JSONField(
        help_text="Published data (JSON payload)",
    )

    # ACK tracking
    wait_for_ack = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether this publish waited for ACK",
    )

    ack_timeout = models.IntegerField(
        null=True,
        blank=True,
        help_text="ACK timeout in seconds",
    )

    acks_received = models.IntegerField(
        default=0,
        help_text="Number of ACKs received",
    )

    acks_expected = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of ACKs expected (if known)",
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
        db_index=True,
        help_text="Current status of publish operation",
    )

    error_code = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Error code if failed",
    )

    error_message = models.TextField(
        null=True,
        blank=True,
        help_text="Error message if failed",
    )

    # Performance
    duration_ms = models.IntegerField(
        null=True,
        blank=True,
        help_text="Total duration in milliseconds",
    )

    # Metadata
    is_notification = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this is a notification (vs other pub type)",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="centrifugo_logs",
        help_text="User who triggered the publish (if applicable)",
    )

    caller_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of caller",
    )

    user_agent = models.TextField(
        null=True,
        blank=True,
        help_text="User agent of caller",
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When publish was initiated",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="When publish completed (success/failure/timeout)",
    )

    class Meta:
        db_table = "django_cfg_centrifugo_log"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["channel", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["wait_for_ack", "status"]),
            models.Index(fields=["user", "-created_at"]),
        ]
        verbose_name = "Centrifugo Log"
        verbose_name_plural = "Centrifugo Logs"

    def __str__(self) -> str:
        """String representation."""
        return f"{self.channel} ({self.message_id[:8]}...) - {self.status}"

    @property
    def is_completed(self) -> bool:
        """Check if publish is completed (any terminal status)."""
        return self.status in [
            self.StatusChoices.SUCCESS,
            self.StatusChoices.FAILED,
            self.StatusChoices.TIMEOUT,
            self.StatusChoices.PARTIAL,
        ]

    @property
    def is_successful(self) -> bool:
        """Check if publish was successful."""
        return self.status == self.StatusChoices.SUCCESS

    @property
    def delivery_rate(self) -> float | None:
        """
        Calculate delivery rate (ACKs received / expected).

        Returns:
            Delivery rate (0.0 to 1.0) or None if unknown
        """
        if self.acks_expected and self.acks_expected > 0:
            return self.acks_received / self.acks_expected
        return None


__all__ = ["CentrifugoLog"]
