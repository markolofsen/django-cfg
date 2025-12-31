"""
gRPC Server Status Model.

Tracks gRPC server lifecycle and heartbeat.
"""

import os
from datetime import timedelta

from django.db import models
from django.utils import timezone


class GRPCServerStatus(models.Model):
    """
    Track gRPC server status and lifecycle.

    Heartbeat interval is configured via GRPCObservabilityConfig.heartbeat_interval (default 300s).
    """

    from ..managers.grpc_server_status import GRPCServerStatusManager

    objects: GRPCServerStatusManager = GRPCServerStatusManager()

    class StatusChoices(models.TextChoices):
        STARTING = "starting", "Starting"
        RUNNING = "running", "Running"
        STOPPING = "stopping", "Stopping"
        STOPPED = "stopped", "Stopped"
        ERROR = "error", "Error"

    # Identity
    instance_id = models.CharField(max_length=100, unique=True, db_index=True)

    # Server config
    host = models.CharField(max_length=200)
    port = models.IntegerField()
    address = models.CharField(max_length=200, db_index=True)
    pid = models.IntegerField()
    hostname = models.CharField(max_length=255)

    # Status
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.STARTING,
        db_index=True,
    )
    error_message = models.TextField(null=True, blank=True)

    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True, db_index=True)
    last_heartbeat = models.DateTimeField(auto_now=True, db_index=True)
    stopped_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "django_cfg_grpc_server_status"
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["status", "-started_at"]),
        ]
        verbose_name = "gRPC Server Status"
        verbose_name_plural = "gRPC Server Statuses"

    def __str__(self) -> str:
        return f"gRPC {self.address} ({self.status}) PID {self.pid}"

    @property
    def is_running(self) -> bool:
        """Check if server is running (status + heartbeat check)."""
        if self.status not in [self.StatusChoices.RUNNING, self.StatusChoices.STARTING]:
            return False

        # Check heartbeat (dead if no heartbeat in 10 minutes)
        if self.last_heartbeat:
            if timezone.now() - self.last_heartbeat > timedelta(minutes=10):
                return False

        return True

    @property
    def uptime_seconds(self) -> int:
        """Server uptime in seconds."""
        if not self.started_at:
            return 0
        end = self.stopped_at or timezone.now()
        return int((end - self.started_at).total_seconds())

    @property
    def uptime_display(self) -> str:
        """Human-readable uptime string."""
        seconds = self.uptime_seconds
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}m {seconds % 60}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"

    def mark_running(self):
        """Mark server as running."""
        self.status = self.StatusChoices.RUNNING
        self.error_message = None
        self.save(update_fields=["status", "error_message", "last_heartbeat"])

    async def amark_running(self):
        """Mark server as running (async)."""
        self.status = self.StatusChoices.RUNNING
        self.error_message = None
        await self.asave(update_fields=["status", "error_message", "last_heartbeat"])

    def mark_stopped(self, error_message: str = None):
        """Mark server as stopped."""
        self.status = self.StatusChoices.STOPPED
        self.stopped_at = timezone.now()
        if error_message:
            self.error_message = error_message
        self.save(update_fields=["status", "stopped_at", "error_message"])

    async def amark_stopped(self, error_message: str = None):
        """Mark server as stopped (async)."""
        self.status = self.StatusChoices.STOPPED
        self.stopped_at = timezone.now()
        if error_message:
            self.error_message = error_message
        await self.asave(update_fields=["status", "stopped_at", "error_message"])

    def heartbeat(self):
        """Update heartbeat timestamp."""
        self.last_heartbeat = timezone.now()
        self.save(update_fields=["last_heartbeat"])


__all__ = ["GRPCServerStatus"]
