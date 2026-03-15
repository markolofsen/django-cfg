"""
GRPCRequestLog Manager.

Custom QuerySet and Manager for GRPCRequestLog model.
"""

from django.db import models
from django.utils import timezone


class GRPCRequestLogQuerySet(models.QuerySet):
    """Custom QuerySet for GRPCRequestLog with filtering helpers."""

    def successful(self):
        """Get all successful logs."""
        return self.filter(status="success")

    def error(self):
        """Get all error logs."""
        return self.filter(status="error")

    def cancelled(self):
        """Get all cancelled logs."""
        return self.filter(status="cancelled")

    def timeout(self):
        """Get all timeout logs."""
        return self.filter(status="timeout")

    def authenticated(self):
        """Get logs for authenticated requests."""
        return self.filter(is_authenticated=True)

    def for_service(self, service_name: str):
        """Get logs for specific service."""
        return self.filter(service_name=service_name)

    def for_method(self, method_name: str):
        """Get logs for specific method."""
        return self.filter(method_name=method_name)

    def for_user(self, user):
        """Get logs for specific user."""
        return self.filter(user=user)

    def recent(self, hours: int = 24):
        """Get logs from recent hours."""
        cutoff = timezone.now() - timezone.timedelta(hours=hours)
        return self.filter(created_at__gte=cutoff)

    def completed(self):
        """Get all completed logs (success, error, cancelled, timeout)."""
        return self.filter(status__in=["success", "error", "cancelled", "timeout"])

    def by_performance(self):
        """Order by duration (fastest first)."""
        return self.filter(duration_ms__isnull=False).order_by("duration_ms")

    def slow_requests(self, threshold_ms: int = 1000):
        """Get slow requests (above threshold)."""
        return self.filter(duration_ms__gt=threshold_ms)


class GRPCRequestLogManager(models.Manager):
    """Custom Manager for GRPCRequestLog."""

    def get_queryset(self):
        """Return custom QuerySet."""
        return GRPCRequestLogQuerySet(self.model, using=self._db)

    def successful(self):
        """Get successful logs."""
        return self.get_queryset().successful()

    def error(self):
        """Get error logs."""
        return self.get_queryset().error()

    def cancelled(self):
        """Get cancelled logs."""
        return self.get_queryset().cancelled()

    def timeout(self):
        """Get timeout logs."""
        return self.get_queryset().timeout()

    def authenticated(self):
        """Get authenticated requests."""
        return self.get_queryset().authenticated()

    def for_service(self, service_name: str):
        """Get logs for service."""
        return self.get_queryset().for_service(service_name)

    def for_method(self, method_name: str):
        """Get logs for method."""
        return self.get_queryset().for_method(method_name)

    def for_user(self, user):
        """Get logs for user."""
        return self.get_queryset().for_user(user)

    def recent(self, hours: int = 24):
        """Get recent logs."""
        return self.get_queryset().recent(hours)

    def slow_requests(self, threshold_ms: int = 1000):
        """Get slow requests."""
        return self.get_queryset().slow_requests(threshold_ms)

    def get_statistics(self, hours: int = 24):
        """
        Get request statistics for recent period.

        Args:
            hours: Number of hours to analyze

        Returns:
            Dictionary with statistics
        """
        recent_logs = self.recent(hours)

        total = recent_logs.count()
        successful = recent_logs.successful().count()
        errors = recent_logs.error().count()
        cancelled = recent_logs.cancelled().count()
        timeout_count = recent_logs.timeout().count()

        success_rate = (successful / total * 100) if total > 0 else 0

        avg_duration = recent_logs.filter(
            duration_ms__isnull=False
        ).aggregate(
            models.Avg("duration_ms")
        )["duration_ms__avg"] or 0

        p95_duration = None
        if total > 0:
            # Calculate 95th percentile
            sorted_durations = list(
                recent_logs.filter(duration_ms__isnull=False)
                .order_by("duration_ms")
                .values_list("duration_ms", flat=True)
            )
            if sorted_durations:
                p95_index = int(len(sorted_durations) * 0.95)
                p95_duration = sorted_durations[p95_index] if p95_index < len(sorted_durations) else sorted_durations[-1]

        return {
            "total": total,
            "successful": successful,
            "errors": errors,
            "cancelled": cancelled,
            "timeout": timeout_count,
            "success_rate": round(success_rate, 2),
            "avg_duration_ms": round(avg_duration, 2),
            "p95_duration_ms": round(p95_duration, 2) if p95_duration else None,
        }

    def mark_success(
        self,
        log_instance,
        duration_ms: int | None = None,
    ):
        """
        Mark request as successful.

        Args:
            log_instance: GRPCRequestLog instance
            duration_ms: Duration in milliseconds
        """
        from ..models import GRPCRequestLog

        log_instance.status = GRPCRequestLog.StatusChoices.SUCCESS
        log_instance.grpc_status_code = "OK"
        log_instance.completed_at = timezone.now()

        if duration_ms is not None:
            log_instance.duration_ms = duration_ms

        log_instance.save(
            update_fields=[
                "status",
                "grpc_status_code",
                "completed_at",
                "duration_ms",
            ]
        )

    async def amark_success(
        self,
        log_instance,
        duration_ms: int | None = None,
        response_data: dict | None = None,
    ):
        """
        Mark request as successful (ASYNC - Django 5.2).

        Args:
            log_instance: GRPCRequestLog instance
            duration_ms: Duration in milliseconds
            response_data: Response data (optional, for future use)
        """
        # NOTE: response_data is accepted but not stored (no field in model yet)
        from ..models import GRPCRequestLog

        log_instance.status = GRPCRequestLog.StatusChoices.SUCCESS
        log_instance.grpc_status_code = "OK"
        log_instance.completed_at = timezone.now()

        if duration_ms is not None:
            log_instance.duration_ms = duration_ms

        await log_instance.asave(
            update_fields=[
                "status",
                "grpc_status_code",
                "completed_at",
                "duration_ms",
            ]
        )

    def mark_error(
        self,
        log_instance,
        grpc_status_code: str,
        error_message: str,
        duration_ms: int | None = None,
    ):
        """
        Mark request as failed.

        Args:
            log_instance: GRPCRequestLog instance
            grpc_status_code: gRPC status code
            error_message: Error message
            duration_ms: Duration in milliseconds
        """
        from ..models import GRPCRequestLog

        log_instance.status = GRPCRequestLog.StatusChoices.ERROR
        log_instance.grpc_status_code = grpc_status_code
        log_instance.error_message = error_message
        log_instance.completed_at = timezone.now()

        if duration_ms is not None:
            log_instance.duration_ms = duration_ms

        log_instance.save(
            update_fields=[
                "status",
                "grpc_status_code",
                "error_message",
                "completed_at",
                "duration_ms",
            ]
        )

    async def amark_error(
        self,
        log_instance,
        grpc_status_code: str,
        error_message: str,
        error_details: dict | None = None,
        duration_ms: int | None = None,
    ):
        """
        Mark request as failed (ASYNC - Django 5.2).

        Args:
            log_instance: GRPCRequestLog instance
            grpc_status_code: gRPC status code
            error_message: Error message
            error_details: Additional error details (JSON)
            duration_ms: Duration in milliseconds
        """
        from ..models import GRPCRequestLog

        log_instance.status = GRPCRequestLog.StatusChoices.ERROR
        log_instance.grpc_status_code = grpc_status_code
        log_instance.error_message = error_message
        log_instance.error_details = error_details
        log_instance.completed_at = timezone.now()

        if duration_ms is not None:
            log_instance.duration_ms = duration_ms

        await log_instance.asave(
            update_fields=[
                "status",
                "grpc_status_code",
                "error_message",
                "error_details",
                "completed_at",
                "duration_ms",
            ]
        )

    def mark_cancelled(
        self,
        log_instance,
        duration_ms: int | None = None,
    ):
        """
        Mark request as cancelled.

        Args:
            log_instance: GRPCRequestLog instance
            duration_ms: Duration in milliseconds
        """
        from ..models import GRPCRequestLog

        log_instance.status = GRPCRequestLog.StatusChoices.CANCELLED
        log_instance.grpc_status_code = "CANCELLED"
        log_instance.completed_at = timezone.now()

        if duration_ms is not None:
            log_instance.duration_ms = duration_ms

        log_instance.save(
            update_fields=["status", "grpc_status_code", "completed_at", "duration_ms"]
        )

    def mark_timeout(
        self,
        log_instance,
        duration_ms: int | None = None,
    ):
        """
        Mark request as timed out.

        Args:
            log_instance: GRPCRequestLog instance
            duration_ms: Duration in milliseconds
        """
        from ..models import GRPCRequestLog

        log_instance.status = GRPCRequestLog.StatusChoices.TIMEOUT
        log_instance.grpc_status_code = "DEADLINE_EXCEEDED"
        log_instance.error_message = "Request timed out"
        log_instance.completed_at = timezone.now()

        if duration_ms is not None:
            log_instance.duration_ms = duration_ms

        log_instance.save(
            update_fields=[
                "status",
                "grpc_status_code",
                "error_message",
                "completed_at",
                "duration_ms",
            ]
        )


__all__ = ["GRPCRequestLogManager", "GRPCRequestLogQuerySet"]
