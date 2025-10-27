"""
CentrifugoLog Manager.

Custom QuerySet and Manager for CentrifugoLog model.
"""

from django.db import models
from django.utils import timezone


class CentrifugoLogQuerySet(models.QuerySet):
    """Custom QuerySet for CentrifugoLog with filtering helpers."""

    def pending(self):
        """Get all pending logs."""
        return self.filter(status="pending")

    def successful(self):
        """Get all successful logs."""
        return self.filter(status="success")

    def failed(self):
        """Get all failed logs."""
        return self.filter(status="failed")

    def timeout(self):
        """Get all timeout logs."""
        return self.filter(status="timeout")

    def with_ack(self):
        """Get logs that waited for ACK."""
        return self.filter(wait_for_ack=True)

    def for_channel(self, channel: str):
        """Get logs for specific channel."""
        return self.filter(channel=channel)

    def for_user(self, user):
        """Get logs for specific user."""
        return self.filter(user=user)

    def recent(self, hours: int = 24):
        """Get logs from recent hours."""
        cutoff = timezone.now() - timezone.timedelta(hours=hours)
        return self.filter(created_at__gte=cutoff)

    def completed(self):
        """Get all completed logs (success, failed, timeout, partial)."""
        return self.exclude(status="pending")

    def by_performance(self):
        """Order by duration (fastest first)."""
        return self.filter(duration_ms__isnull=False).order_by("duration_ms")


class CentrifugoLogManager(models.Manager):
    """Custom Manager for CentrifugoLog."""

    def get_queryset(self):
        """Return custom QuerySet."""
        return CentrifugoLogQuerySet(self.model, using=self._db)

    def pending(self):
        """Get pending logs."""
        return self.get_queryset().pending()

    def successful(self):
        """Get successful logs."""
        return self.get_queryset().successful()

    def failed(self):
        """Get failed logs."""
        return self.get_queryset().failed()

    def timeout(self):
        """Get timeout logs."""
        return self.get_queryset().timeout()

    def with_ack(self):
        """Get logs with ACK tracking."""
        return self.get_queryset().with_ack()

    def for_channel(self, channel: str):
        """Get logs for channel."""
        return self.get_queryset().for_channel(channel)

    def for_user(self, user):
        """Get logs for user."""
        return self.get_queryset().for_user(user)

    def recent(self, hours: int = 24):
        """Get recent logs."""
        return self.get_queryset().recent(hours)

    def get_statistics(self, hours: int = 24):
        """
        Get publish statistics for recent period.

        Args:
            hours: Number of hours to analyze

        Returns:
            Dictionary with statistics
        """
        # Get all recent logs (not just with_ack) to include fire-and-forget publishes
        recent_logs = self.recent(hours)

        total = recent_logs.count()
        successful = recent_logs.successful().count()
        failed = recent_logs.failed().count()
        timeout_count = recent_logs.timeout().count()

        success_rate = (successful / total * 100) if total > 0 else 0

        avg_duration = recent_logs.filter(
            duration_ms__isnull=False
        ).aggregate(
            models.Avg("duration_ms")
        )["duration_ms__avg"] or 0

        avg_acks = recent_logs.aggregate(
            models.Avg("acks_received")
        )["acks_received__avg"] or 0

        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "timeout": timeout_count,
            "success_rate": round(success_rate, 2),
            "avg_duration_ms": round(avg_duration, 2),
            "avg_acks_received": round(avg_acks, 2),
        }

    def mark_success(self, log_instance, acks_received: int = 0, duration_ms: int | None = None):
        """
        Mark publish as successful.

        Args:
            log_instance: CentrifugoLog instance
            acks_received: Number of ACKs received
            duration_ms: Duration in milliseconds
        """
        from ..models import CentrifugoLog

        log_instance.status = CentrifugoLog.StatusChoices.SUCCESS
        log_instance.acks_received = acks_received
        log_instance.completed_at = timezone.now()

        if duration_ms is not None:
            log_instance.duration_ms = duration_ms

        log_instance.save(update_fields=["status", "acks_received", "completed_at", "duration_ms"])

    def mark_partial(
        self,
        log_instance,
        acks_received: int,
        acks_expected: int,
        duration_ms: int | None = None,
    ):
        """
        Mark publish as partially delivered.

        Args:
            log_instance: CentrifugoLog instance
            acks_received: Number of ACKs received
            acks_expected: Number of ACKs expected
            duration_ms: Duration in milliseconds
        """
        from ..models import CentrifugoLog

        log_instance.status = CentrifugoLog.StatusChoices.PARTIAL
        log_instance.acks_received = acks_received
        log_instance.acks_expected = acks_expected
        log_instance.completed_at = timezone.now()

        if duration_ms is not None:
            log_instance.duration_ms = duration_ms

        log_instance.save(
            update_fields=[
                "status",
                "acks_received",
                "acks_expected",
                "completed_at",
                "duration_ms",
            ]
        )

    def mark_failed(
        self,
        log_instance,
        error_code: str,
        error_message: str,
        duration_ms: int | None = None,
    ):
        """
        Mark publish as failed.

        Args:
            log_instance: CentrifugoLog instance
            error_code: Error code
            error_message: Error message
            duration_ms: Duration in milliseconds
        """
        from ..models import CentrifugoLog

        log_instance.status = CentrifugoLog.StatusChoices.FAILED
        log_instance.error_code = error_code
        log_instance.error_message = error_message
        log_instance.completed_at = timezone.now()

        if duration_ms is not None:
            log_instance.duration_ms = duration_ms

        log_instance.save(
            update_fields=[
                "status",
                "error_code",
                "error_message",
                "completed_at",
                "duration_ms",
            ]
        )

    def mark_timeout(
        self,
        log_instance,
        acks_received: int = 0,
        duration_ms: int | None = None,
    ):
        """
        Mark publish as timed out.

        Args:
            log_instance: CentrifugoLog instance
            acks_received: Number of ACKs received before timeout
            duration_ms: Duration in milliseconds
        """
        from ..models import CentrifugoLog

        log_instance.status = CentrifugoLog.StatusChoices.TIMEOUT
        log_instance.acks_received = acks_received
        log_instance.error_code = "timeout"
        log_instance.error_message = f"Timeout after {log_instance.ack_timeout}s"
        log_instance.completed_at = timezone.now()

        if duration_ms is not None:
            log_instance.duration_ms = duration_ms

        log_instance.save(
            update_fields=[
                "status",
                "acks_received",
                "error_code",
                "error_message",
                "completed_at",
                "duration_ms",
            ]
        )


__all__ = ["CentrifugoLogManager", "CentrifugoLogQuerySet"]
