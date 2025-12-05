"""
TerminalSession model - Represents an active terminal session.
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class TerminalSession(models.Model):
    """
    Terminal session - connection between browser and Electron.

    Flow:
    1. Browser opens terminal → creates TerminalSession
    2. Electron connects via gRPC → registers with session_id
    3. Bidirectional streaming established
    4. Commands flow: Browser → WebSocket → Django → gRPC → Electron
    5. Output flows: Electron → gRPC → Django → WebSocket → Browser
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONNECTED = 'connected', 'Connected'
        DISCONNECTED = 'disconnected', 'Disconnected'
        ERROR = 'error', 'Error'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Owner (optional for auto-created sessions from Electron)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='terminal_sessions',
        null=True,
        blank=True,
        help_text="Session owner (null for auto-created sessions)"
    )

    # Session info
    name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Session display name"
    )

    # Connection status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        help_text="Current session status"
    )

    # Electron client info
    electron_hostname = models.CharField(
        max_length=255,
        blank=True,
        help_text="Connected Electron client hostname"
    )
    electron_version = models.CharField(
        max_length=50,
        blank=True,
        help_text="Electron client version"
    )

    # Working directory
    working_directory = models.CharField(
        max_length=500,
        default='~',
        help_text="Current working directory in terminal"
    )

    # Shell settings
    shell = models.CharField(
        max_length=100,
        default='/bin/zsh',
        help_text="Shell to use (e.g., /bin/bash, /bin/zsh)"
    )

    # Environment variables (JSON)
    environment = models.JSONField(
        default=dict,
        blank=True,
        help_text="Environment variables for the session"
    )

    # Statistics
    commands_count = models.PositiveIntegerField(
        default=0,
        help_text="Total commands executed in this session"
    )
    bytes_sent = models.PositiveBigIntegerField(
        default=0,
        help_text="Total bytes sent to terminal"
    )
    bytes_received = models.PositiveBigIntegerField(
        default=0,
        help_text="Total bytes received from terminal"
    )

    # Timestamps
    connected_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When Electron client connected"
    )
    last_heartbeat_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last heartbeat from Electron"
    )
    disconnected_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When session was disconnected"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Terminal Session'
        verbose_name_plural = 'Terminal Sessions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self) -> str:
        username = self.user.username if self.user else 'Anonymous'
        return f"{username} - {self.name or self.id}"

    @property
    def is_active(self) -> bool:
        """Check if session is currently active."""
        return self.status == self.Status.CONNECTED

    @property
    def heartbeat_age_seconds(self) -> float:
        """Get seconds since last heartbeat."""
        if not self.last_heartbeat_at:
            return float('inf')
        from django.utils import timezone
        delta = timezone.now() - self.last_heartbeat_at
        return delta.total_seconds()

    @property
    def is_alive(self) -> bool:
        """
        Check if session is truly alive (recent heartbeat).

        Session is alive if:
        - Status is CONNECTED
        - Last heartbeat was within 60 seconds (2x heartbeat interval of 30s)
        """
        if self.status != self.Status.CONNECTED:
            return False
        return self.heartbeat_age_seconds < 60

    @property
    def display_name(self) -> str:
        """Get display name for UI."""
        if self.name:
            return self.name
        return f"Session {str(self.id)[:8]}"
