"""
CommandHistory model - Stores executed commands and their output.
"""

import uuid
from django.db import models
from .session import TerminalSession


class CommandHistory(models.Model):
    """
    Command history entry.

    Stores each command executed in a terminal session
    along with its output, exit code, and timing.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        RUNNING = 'running', 'Running'
        SUCCESS = 'success', 'Success'
        FAILED = 'failed', 'Failed'
        CANCELLED = 'cancelled', 'Cancelled'
        TIMEOUT = 'timeout', 'Timeout'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Parent session
    session = models.ForeignKey(
        TerminalSession,
        on_delete=models.CASCADE,
        related_name='commands',
        help_text="Terminal session"
    )

    # Command info
    command = models.TextField(help_text="Executed command")

    # Working directory at execution time
    working_directory = models.CharField(
        max_length=500,
        blank=True,
        help_text="Working directory when command was executed"
    )

    # Execution status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        help_text="Command execution status"
    )

    # Output (stored as text, can be large)
    stdout = models.TextField(
        blank=True,
        help_text="Standard output"
    )
    stderr = models.TextField(
        blank=True,
        help_text="Standard error"
    )

    # Exit code
    exit_code = models.IntegerField(
        null=True,
        blank=True,
        help_text="Process exit code"
    )

    # Timing
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When command started executing"
    )
    finished_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When command finished"
    )

    # Bytes transferred
    bytes_in = models.PositiveIntegerField(
        default=0,
        help_text="Bytes sent to process (stdin)"
    )
    bytes_out = models.PositiveIntegerField(
        default=0,
        help_text="Bytes received from process (stdout+stderr)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Command History'
        verbose_name_plural = 'Command History'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['session', '-created_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self) -> str:
        cmd_preview = self.command[:50] + '...' if len(self.command) > 50 else self.command
        return f"[{self.status}] {cmd_preview}"

    @property
    def duration_ms(self) -> int | None:
        """Get execution duration in milliseconds."""
        if self.started_at and self.finished_at:
            delta = self.finished_at - self.started_at
            return int(delta.total_seconds() * 1000)
        return None

    @property
    def is_success(self) -> bool:
        """Check if command completed successfully."""
        return self.status == self.Status.SUCCESS and self.exit_code == 0

    @property
    def output_preview(self) -> str:
        """Get preview of output for display."""
        output = self.stdout or self.stderr or ''
        if len(output) > 100:
            return output[:100] + '...'
        return output
