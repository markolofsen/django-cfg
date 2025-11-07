"""
gRPC Server Status Model.

Tracks the lifecycle and status of gRPC server instances.
Provides real-time monitoring of server availability and uptime.
"""

import os
from datetime import datetime, timedelta

from django.db import models
from django.utils import timezone


class GRPCServerStatus(models.Model):
    """
    Track gRPC server status and lifecycle.

    Stores information about server instances including:
    - Start/stop times
    - Process ID
    - Server address and configuration
    - Health status and heartbeats

    Example:
        >>> # Server starts
        >>> status = GRPCServerStatus.objects.start_server(
        ...     host="[::]",
        ...     port=50051,
        ...     pid=12345
        ... )
        >>> status.is_running
        True
        >>> status.uptime_seconds
        120

        >>> # Server stops
        >>> status.stop_server()
        >>> status.is_running
        False
    """

    # Custom manager
    from ..managers.grpc_server_status import GRPCServerStatusManager

    objects: GRPCServerStatusManager = GRPCServerStatusManager()

    class StatusChoices(models.TextChoices):
        """Server status choices."""

        STARTING = "starting", "Starting"
        RUNNING = "running", "Running"
        STOPPING = "stopping", "Stopping"
        STOPPED = "stopped", "Stopped"
        ERROR = "error", "Error"

    # Identity
    instance_id = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Unique instance identifier (hostname:port:pid)",
    )

    # Server configuration
    host = models.CharField(
        max_length=200,
        help_text="Server host address",
    )

    port = models.IntegerField(
        help_text="Server port",
    )

    address = models.CharField(
        max_length=200,
        db_index=True,
        help_text="Full server address (host:port)",
    )

    # Process information
    pid = models.IntegerField(
        help_text="Process ID of gRPC server",
    )

    hostname = models.CharField(
        max_length=255,
        help_text="Server hostname",
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.STARTING,
        db_index=True,
        help_text="Current server status",
    )

    # Lifecycle timestamps
    started_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When server started",
    )

    last_heartbeat = models.DateTimeField(
        auto_now=True,
        db_index=True,
        help_text="Last heartbeat timestamp",
    )

    stopped_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When server stopped",
    )

    # Configuration snapshot
    max_workers = models.IntegerField(
        default=10,
        help_text="Maximum worker threads",
    )

    enable_reflection = models.BooleanField(
        default=False,
        help_text="Whether reflection is enabled",
    )

    # Registered services (stored as JSON)
    registered_services = models.JSONField(
        default=list,
        blank=True,
        help_text="List of registered service metadata (name, methods, etc.)",
    )

    enable_health_check = models.BooleanField(
        default=True,
        help_text="Whether health check is enabled",
    )

    # Error tracking
    error_message = models.TextField(
        null=True,
        blank=True,
        help_text="Error message if status is ERROR",
    )

    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Record creation time",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Record last update time",
    )

    class Meta:
        db_table = "django_cfg_grpc_server_status"
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["status", "-started_at"]),
            models.Index(fields=["address", "-started_at"]),
            models.Index(fields=["pid", "-started_at"]),
        ]
        verbose_name = "gRPC Server Status"
        verbose_name_plural = "gRPC Server Statuses"

    def __str__(self) -> str:
        """String representation."""
        return f"gRPC Server {self.address} ({self.status}) - PID {self.pid}"

    @property
    def is_running(self) -> bool:
        """
        Check if server is currently running.

        Uses environment-aware detection:
        - Production: Assumes external server (Docker), relies on heartbeat only
        - Development/Test: Checks local process + heartbeat
        """
        if self.status not in [self.StatusChoices.RUNNING, self.StatusChoices.STARTING]:
            return False

        # Check if process is still alive (auto-detects external servers)
        if not self._is_process_alive():
            return False

        # Check heartbeat (consider dead if no heartbeat in 5 minutes)
        if self.last_heartbeat:
            time_since_heartbeat = timezone.now() - self.last_heartbeat
            if time_since_heartbeat > timedelta(minutes=5):
                return False

        return True

    @property
    def uptime_seconds(self) -> int:
        """Calculate server uptime in seconds."""
        if not self.is_running or not self.started_at:
            return 0

        if self.stopped_at:
            delta = self.stopped_at - self.started_at
        else:
            delta = timezone.now() - self.started_at

        return int(delta.total_seconds())

    @property
    def uptime_display(self) -> str:
        """Human-readable uptime."""
        seconds = self.uptime_seconds
        if seconds == 0:
            return "Not running"

        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if seconds > 0 or not parts:
            parts.append(f"{seconds}s")

        return " ".join(parts)

    def _is_process_alive(self) -> bool:
        """
        Check if the process is still running.

        Uses environment-aware detection:
        - Production mode: Skip PID check (assumes external server in Docker)
        - Development/Test: Check PID with graceful fallback for containers
        """
        try:
            from django_cfg.core import get_current_config

            # Auto-detect based on env_mode
            config = get_current_config()
            if config and str(config.env_mode) == "production":
                # Production = external server in separate container
                # Don't check PID, rely on heartbeat only
                return True

        except Exception:
            # Config not available, use fallback logic
            pass

        # Development/Test or fallback: check PID with graceful handling
        try:
            # Send signal 0 to check if process exists
            os.kill(self.pid, 0)
            return True
        except ProcessLookupError:
            # PID not found - could be different namespace (Docker)
            # Don't mark as dead immediately, rely on heartbeat
            return True
        except PermissionError:
            # Process exists but no permission to signal
            return True
        except OSError:
            # Other OS error (e.g., process died)
            return False

    def mark_running(self):
        """Mark server as running (SYNC)."""
        self.status = self.StatusChoices.RUNNING
        self.error_message = None
        self.save(update_fields=["status", "error_message", "updated_at", "last_heartbeat"])

    async def amark_running(self):
        """Mark server as running (ASYNC - Django 5.2)."""
        self.status = self.StatusChoices.RUNNING
        self.error_message = None
        await self.asave(update_fields=["status", "error_message", "updated_at", "last_heartbeat"])

    def mark_stopping(self):
        """Mark server as stopping (SYNC)."""
        self.status = self.StatusChoices.STOPPING
        self.save(update_fields=["status", "updated_at", "last_heartbeat"])

    async def amark_stopping(self):
        """Mark server as stopping (ASYNC - Django 5.2)."""
        self.status = self.StatusChoices.STOPPING
        await self.asave(update_fields=["status", "updated_at", "last_heartbeat"])

    def mark_stopped(self, error_message: str = None):
        """Mark server as stopped (SYNC)."""
        self.status = self.StatusChoices.STOPPED
        self.stopped_at = timezone.now()
        if error_message:
            self.error_message = error_message
        self.save(update_fields=["status", "stopped_at", "error_message", "updated_at"])

    async def amark_stopped(self, error_message: str = None):
        """Mark server as stopped (ASYNC - Django 5.2)."""
        self.status = self.StatusChoices.STOPPED
        self.stopped_at = timezone.now()
        if error_message:
            self.error_message = error_message
        await self.asave(update_fields=["status", "stopped_at", "error_message", "updated_at"])

    def mark_error(self, error_message: str):
        """Mark server as error."""
        self.status = self.StatusChoices.ERROR
        self.error_message = error_message
        self.stopped_at = timezone.now()
        self.save(update_fields=["status", "error_message", "stopped_at", "updated_at"])

    def heartbeat(self):
        """Update heartbeat timestamp."""
        self.last_heartbeat = timezone.now()
        self.save(update_fields=["last_heartbeat", "updated_at"])


__all__ = ["GRPCServerStatus"]
