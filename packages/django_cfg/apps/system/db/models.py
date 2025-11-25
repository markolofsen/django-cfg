"""
Database Backup Models.

Stores backup records and metadata for tracking and management.
"""

import uuid
from django.db import models
from django.utils import timezone


class BackupRecord(models.Model):
    """
    Record of a database backup.

    Tracks backup metadata, status, and storage location.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        DELETED = "deleted", "Deleted"

    class DatabaseEngine(models.TextChoices):
        POSTGRESQL = "postgresql", "PostgreSQL"
        MYSQL = "mysql", "MySQL"
        SQLITE = "sqlite", "SQLite"
        UNKNOWN = "unknown", "Unknown"

    class StorageBackend(models.TextChoices):
        LOCAL = "local", "Local"
        S3 = "s3", "S3"

    # Primary key
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # Database info
    database_alias = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Django database alias",
    )

    database_name = models.CharField(
        max_length=255,
        help_text="Actual database name",
    )

    database_engine = models.CharField(
        max_length=20,
        choices=DatabaseEngine.choices,
        default=DatabaseEngine.UNKNOWN,
        help_text="Database engine type",
    )

    # Backup info
    filename = models.CharField(
        max_length=500,
        help_text="Backup filename",
    )

    file_path = models.TextField(
        help_text="Full path or S3 key to backup file",
    )

    file_size = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Backup file size in bytes",
    )

    compression = models.CharField(
        max_length=10,
        default="gzip",
        help_text="Compression algorithm used",
    )

    encrypted = models.BooleanField(
        default=False,
        help_text="Whether backup is encrypted",
    )

    # Storage info
    storage_backend = models.CharField(
        max_length=10,
        choices=StorageBackend.choices,
        default=StorageBackend.LOCAL,
        help_text="Storage backend type",
    )

    storage_bucket = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="S3 bucket name (if S3 storage)",
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        help_text="Backup status",
    )

    error_message = models.TextField(
        blank=True,
        default="",
        help_text="Error message if failed",
    )

    # Timing
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When backup started",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When backup completed",
    )

    duration_seconds = models.FloatField(
        null=True,
        blank=True,
        help_text="Backup duration in seconds",
    )

    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    is_scheduled = models.BooleanField(
        default=False,
        help_text="Whether backup was created by scheduler",
    )

    is_manual = models.BooleanField(
        default=False,
        help_text="Whether backup was created manually",
    )

    tables_count = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of tables backed up",
    )

    rows_count = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Approximate number of rows backed up",
    )

    checksum = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text="SHA256 checksum of backup file",
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional backup metadata",
    )

    class Meta:
        app_label = "db_backup"
        verbose_name = "Backup Record"
        verbose_name_plural = "Backup Records"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["database_alias", "status"]),
            models.Index(fields=["created_at", "status"]),
            models.Index(fields=["storage_backend", "status"]),
        ]

    def __str__(self):
        return f"{self.database_alias} - {self.filename} ({self.status})"

    @property
    def file_size_human(self) -> str:
        """Return human-readable file size."""
        if not self.file_size:
            return "N/A"
        size = self.file_size
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if abs(size) < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"

    @property
    def duration_human(self) -> str:
        """Return human-readable duration."""
        if not self.duration_seconds:
            return "N/A"
        seconds = self.duration_seconds
        if seconds < 60:
            return f"{seconds:.1f}s"
        minutes = seconds / 60
        if minutes < 60:
            return f"{minutes:.1f}m"
        hours = minutes / 60
        return f"{hours:.1f}h"

    def mark_running(self):
        """Mark backup as running."""
        self.status = self.Status.RUNNING
        self.started_at = timezone.now()
        self.save(update_fields=["status", "started_at"])

    def mark_completed(self, file_size: int = None, checksum: str = None):
        """Mark backup as completed."""
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        if self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
        if file_size:
            self.file_size = file_size
        if checksum:
            self.checksum = checksum
        self.save(update_fields=[
            "status", "completed_at", "duration_seconds", "file_size", "checksum"
        ])

    def mark_failed(self, error: str):
        """Mark backup as failed."""
        self.status = self.Status.FAILED
        self.completed_at = timezone.now()
        self.error_message = error
        if self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
        self.save(update_fields=[
            "status", "completed_at", "duration_seconds", "error_message"
        ])

    def mark_deleted(self):
        """Mark backup as deleted (file removed)."""
        self.status = self.Status.DELETED
        self.save(update_fields=["status"])


class RestoreRecord(models.Model):
    """
    Record of a database restore operation.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    # Primary key
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # Reference to backup
    backup = models.ForeignKey(
        BackupRecord,
        on_delete=models.SET_NULL,
        null=True,
        related_name="restores",
        help_text="Source backup record",
    )

    # Target database
    target_database_alias = models.CharField(
        max_length=100,
        help_text="Target Django database alias",
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    error_message = models.TextField(
        blank=True,
        default="",
    )

    # Timing
    started_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    duration_seconds = models.FloatField(
        null=True,
        blank=True,
    )

    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    created_by = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="User or system that initiated restore",
    )

    class Meta:
        app_label = "db_backup"
        verbose_name = "Restore Record"
        verbose_name_plural = "Restore Records"
        ordering = ["-created_at"]

    def __str__(self):
        backup_name = self.backup.filename if self.backup else "Unknown"
        return f"Restore {backup_name} -> {self.target_database_alias} ({self.status})"

    def mark_running(self):
        """Mark restore as running."""
        self.status = self.Status.RUNNING
        self.started_at = timezone.now()
        self.save(update_fields=["status", "started_at"])

    def mark_completed(self):
        """Mark restore as completed."""
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        if self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
        self.save(update_fields=["status", "completed_at", "duration_seconds"])

    def mark_failed(self, error: str):
        """Mark restore as failed."""
        self.status = self.Status.FAILED
        self.completed_at = timezone.now()
        self.error_message = error
        if self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
        self.save(update_fields=[
            "status", "completed_at", "duration_seconds", "error_message"
        ])
