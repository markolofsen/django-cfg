"""
gRPC Request Log Model.

Django model for tracking gRPC requests and responses.
Provides observability for debugging and monitoring.
"""

from django.conf import settings
from django.db import models
from django.utils import timezone

from .grpc_api_key import GrpcApiKey

class GRPCRequestLog(models.Model):
    """
    Log of gRPC requests and responses.

    Tracks all gRPC method calls with status, timing, and error tracking.
    Provides observability for debugging and monitoring.

    Example:
        >>> log = GRPCRequestLog.objects.create(
        ...     request_id="abc123",
        ...     service_name="myapp.UserService",
        ...     method_name="GetUser",
        ... )
        >>> log.mark_success(duration_ms=125)
    """

    # Custom manager
    from ..managers.grpc_request_log import GRPCRequestLogManager

    objects: GRPCRequestLogManager = GRPCRequestLogManager()

    class StatusChoices(models.TextChoices):
        """Status of gRPC request."""

        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        ERROR = "error", "Error"
        CANCELLED = "cancelled", "Cancelled"
        TIMEOUT = "timeout", "Timeout"

    # Identity
    request_id = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Unique request identifier (UUID)",
    )

    # gRPC details
    service_name = models.CharField(
        max_length=200,
        db_index=True,
        help_text="gRPC service name (e.g., myapp.UserService)",
    )

    method_name = models.CharField(
        max_length=200,
        db_index=True,
        help_text="gRPC method name (e.g., GetUser)",
    )

    full_method = models.CharField(
        max_length=400,
        db_index=True,
        help_text="Full method path (e.g., /myapp.UserService/GetUser)",
    )

    # Request/Response data
    request_size = models.IntegerField(
        null=True,
        blank=True,
        help_text="Request size in bytes",
    )

    response_size = models.IntegerField(
        null=True,
        blank=True,
        help_text="Response size in bytes",
    )

    request_data = models.JSONField(
        null=True,
        blank=True,
        help_text="Request data (if logged)",
    )

    response_data = models.JSONField(
        null=True,
        blank=True,
        help_text="Response data (if logged)",
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
        db_index=True,
        help_text="Current status of request",
    )

    grpc_status_code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_index=True,
        help_text="gRPC status code (OK, CANCELLED, INVALID_ARGUMENT, etc.)",
    )

    error_message = models.TextField(
        null=True,
        blank=True,
        help_text="Error message if failed",
    )

    error_details = models.JSONField(
        null=True,
        blank=True,
        help_text="Additional error details",
    )

    # Performance
    duration_ms = models.IntegerField(
        null=True,
        blank=True,
        help_text="Total duration in milliseconds",
    )

    # User context
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="grpc_request_logs",
        help_text="Authenticated user (if applicable)",
    )

    api_key = models.ForeignKey(
        GrpcApiKey,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="request_logs",
        help_text="API key used for authentication (if applicable)",
    )

    is_authenticated = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether request was authenticated",
    )

    # Client metadata
    client_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="Client IP address",
    )

    user_agent = models.TextField(
        null=True,
        blank=True,
        help_text="User agent from metadata",
    )

    peer = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="gRPC peer information",
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When request was received",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="When request completed (success/error)",
    )

    class Meta:
        db_table = "django_cfg_grpc_request_log"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["service_name", "-created_at"]),
            models.Index(fields=["method_name", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["api_key", "-created_at"]),
            models.Index(fields=["grpc_status_code", "-created_at"]),
        ]
        verbose_name = "gRPC Request Log"
        verbose_name_plural = "gRPC Request Logs"

    def __str__(self) -> str:
        """String representation."""
        return f"{self.full_method} ({self.request_id[:8]}...) - {self.status}"

    @property
    def is_completed(self) -> bool:
        """Check if request is completed (any terminal status)."""
        return self.status in [
            self.StatusChoices.SUCCESS,
            self.StatusChoices.ERROR,
            self.StatusChoices.CANCELLED,
            self.StatusChoices.TIMEOUT,
        ]

    @property
    def is_successful(self) -> bool:
        """Check if request was successful."""
        return self.status == self.StatusChoices.SUCCESS

    @property
    def success_rate(self) -> float:
        """Calculate success rate (for compatibility with stats)."""
        return 1.0 if self.is_successful else 0.0


__all__ = ["GRPCRequestLog"]
