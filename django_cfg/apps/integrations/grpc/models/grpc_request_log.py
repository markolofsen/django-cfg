"""
gRPC Request Log Model.

Tracks gRPC requests for monitoring (unary calls only, streaming disabled by default).
"""

from django.conf import settings
from django.db import models

from .grpc_api_key import GrpcApiKey


class GRPCRequestLog(models.Model):
    """
    Log of gRPC requests.

    Note: Streaming calls are NOT logged by default (see GRPCObservabilityConfig).
    """

    from ..managers.grpc_request_log import GRPCRequestLogManager

    objects: GRPCRequestLogManager = GRPCRequestLogManager()

    class StatusChoices(models.TextChoices):
        SUCCESS = "success", "Success"
        ERROR = "error", "Error"
        CANCELLED = "cancelled", "Cancelled"
        TIMEOUT = "timeout", "Timeout"

    # Identity
    request_id = models.CharField(max_length=100, unique=True, db_index=True)

    # gRPC details
    service_name = models.CharField(max_length=200, db_index=True)
    method_name = models.CharField(max_length=200, db_index=True)
    full_method = models.CharField(max_length=400, db_index=True)

    # Status
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.SUCCESS,
        db_index=True,
    )
    grpc_status_code = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    error_message = models.TextField(null=True, blank=True)
    error_details = models.JSONField(null=True, blank=True)

    # Performance
    duration_ms = models.IntegerField(null=True, blank=True)

    # Auth context
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="grpc_request_logs",
    )
    api_key = models.ForeignKey(
        GrpcApiKey,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="request_logs",
    )
    is_authenticated = models.BooleanField(default=False, db_index=True)

    # Client
    client_ip = models.GenericIPAddressField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "django_cfg_grpc_request_log"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["service_name", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
        ]
        verbose_name = "gRPC Request Log"
        verbose_name_plural = "gRPC Request Logs"

    def __str__(self) -> str:
        return f"{self.full_method} ({self.request_id[:8]}...) - {self.status}"

    @property
    def is_successful(self) -> bool:
        return self.status == self.StatusChoices.SUCCESS


__all__ = ["GRPCRequestLog"]
