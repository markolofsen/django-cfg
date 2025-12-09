"""
Database backup configuration models for django_cfg.

Supports:
- PostgreSQL (pg_dump/pg_restore)
- MySQL (mysqldump/mysql)
- SQLite (file copy)

Storage backends:
- Local filesystem
- S3-compatible (AWS S3, Cloudflare R2, MinIO)

Scheduling:
- Auto-scheduling via Django-RQ if enabled
- Manual backup via management commands
"""

from datetime import time
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class BackupStorageConfig(BaseModel):
    """
    Backup storage destination configuration.

    Supports local filesystem and S3-compatible storage.
    """

    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True,
        "extra": "forbid",
    }

    # Storage type
    backend: Literal["local", "s3"] = Field(
        default="local",
        description="Storage backend type",
    )

    # Local storage settings
    local_path: str = Field(
        default="backups/",
        description="Local directory for backups (relative to BASE_DIR or absolute)",
    )

    # S3-compatible storage settings
    s3_bucket: Optional[str] = Field(
        default=None,
        description="S3 bucket name",
    )

    s3_endpoint_url: Optional[str] = Field(
        default=None,
        description="S3 endpoint URL (for R2, MinIO, etc.)",
    )

    s3_access_key: Optional[str] = Field(
        default=None,
        description="S3 access key ID",
        repr=False,
    )

    s3_secret_key: Optional[str] = Field(
        default=None,
        description="S3 secret access key",
        repr=False,
    )

    s3_region: str = Field(
        default="auto",
        description="S3 region (use 'auto' for R2)",
    )

    s3_prefix: str = Field(
        default="db-backups/",
        description="S3 key prefix for backups",
    )

    @model_validator(mode="after")
    def validate_storage_config(self) -> "BackupStorageConfig":
        """Validate storage configuration consistency."""
        if self.backend == "s3":
            if not self.s3_bucket:
                raise ValueError("s3_bucket is required for S3 backend")
            if not self.s3_access_key or not self.s3_secret_key:
                raise ValueError("s3_access_key and s3_secret_key are required for S3 backend")
        return self


class BackupScheduleConfig(BaseModel):
    """
    Backup schedule configuration.

    Supports cron expressions and simple intervals.
    """

    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True,
        "extra": "forbid",
    }

    # Enable/disable
    enabled: bool = Field(
        default=True,
        description="Enable scheduled backups",
    )

    # Cron expression (preferred)
    cron: Optional[str] = Field(
        default=None,
        description="Cron expression (e.g., '0 2 * * *' for daily at 2 AM)",
    )

    # Simple interval (alternative to cron)
    interval_hours: Optional[int] = Field(
        default=None,
        description="Backup interval in hours (alternative to cron)",
        ge=1,
        le=168,  # Max 1 week
    )

    # Daily backup time (alternative to cron)
    daily_time: Optional[time] = Field(
        default=None,
        description="Daily backup time (HH:MM)",
    )

    # Queue for RQ
    queue: str = Field(
        default="default",
        description="RQ queue for backup jobs",
    )

    @model_validator(mode="after")
    def validate_schedule_config(self) -> "BackupScheduleConfig":
        """Validate schedule configuration."""
        if self.enabled:
            options = [self.cron, self.interval_hours, self.daily_time]
            specified = [o for o in options if o is not None]
            if len(specified) == 0:
                # Default to daily at 2 AM
                object.__setattr__(self, "cron", "0 2 * * *")
            elif len(specified) > 1:
                raise ValueError("Specify only one of: cron, interval_hours, daily_time")
        return self

    def to_cron_expression(self) -> Optional[str]:
        """Convert schedule to cron expression."""
        if not self.enabled:
            return None
        if self.cron:
            return self.cron
        if self.daily_time:
            return f"{self.daily_time.minute} {self.daily_time.hour} * * *"
        if self.interval_hours:
            return f"0 */{self.interval_hours} * * *"
        return "0 2 * * *"  # Default


class BackupRetentionConfig(BaseModel):
    """
    Backup retention policy configuration.
    """

    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True,
        "extra": "forbid",
    }

    # Enable auto-cleanup
    enabled: bool = Field(
        default=True,
        description="Enable automatic backup cleanup",
    )

    # Retention periods
    keep_daily: int = Field(
        default=7,
        description="Number of daily backups to keep",
        ge=1,
        le=365,
    )

    keep_weekly: int = Field(
        default=4,
        description="Number of weekly backups to keep",
        ge=0,
        le=52,
    )

    keep_monthly: int = Field(
        default=3,
        description="Number of monthly backups to keep",
        ge=0,
        le=24,
    )

    # Size limit (MB)
    max_total_size_mb: Optional[int] = Field(
        default=None,
        description="Maximum total backup size in MB (None = unlimited)",
        ge=100,
    )


class BackupDatabaseConfig(BaseModel):
    """
    Per-database backup configuration.

    Allows overriding global settings for specific databases.
    """

    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True,
        "extra": "forbid",
    }

    # Database alias (from Django DATABASES)
    alias: str = Field(
        ...,
        description="Database alias from Django settings",
    )

    # Enable/disable backup for this database
    enabled: bool = Field(
        default=True,
        description="Enable backups for this database",
    )

    # Tables to exclude
    exclude_tables: List[str] = Field(
        default_factory=list,
        description="Tables to exclude from backup",
    )

    # Include only specific tables (empty = all)
    include_tables: List[str] = Field(
        default_factory=list,
        description="Tables to include (empty = all tables)",
    )

    # Custom dump options
    extra_options: List[str] = Field(
        default_factory=list,
        description="Extra command-line options for dump tool",
    )

    # Override schedule for this database
    schedule_override: Optional[BackupScheduleConfig] = Field(
        default=None,
        description="Override global schedule for this database",
    )


class BackupConfig(BaseModel):
    """
    Main database backup configuration.

    Example:
        ```python
        from django_cfg.models import BackupConfig, BackupStorageConfig

        class MyConfig(DjangoConfig):
            backup: BackupConfig = BackupConfig(
                enabled=True,
                storage=BackupStorageConfig(
                    backend="s3",
                    s3_bucket="my-backups",
                    s3_endpoint_url="https://xxx.r2.cloudflarestorage.com",
                    s3_access_key="${R2_ACCESS_KEY}",
                    s3_secret_key="${R2_SECRET_KEY}",
                ),
                schedule=BackupScheduleConfig(
                    cron="0 2 * * *",  # Daily at 2 AM
                ),
                retention=BackupRetentionConfig(
                    keep_daily=7,
                    keep_weekly=4,
                ),
            )
        ```
    """

    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True,
        "extra": "forbid",
    }

    # Enable/disable backup module
    enabled: bool = Field(
        default=False,
        description="Enable database backup module",
    )

    # Storage configuration
    storage: BackupStorageConfig = Field(
        default_factory=BackupStorageConfig,
        description="Backup storage configuration",
    )

    # Schedule configuration
    schedule: BackupScheduleConfig = Field(
        default_factory=BackupScheduleConfig,
        description="Backup schedule configuration",
    )

    # Retention configuration
    retention: BackupRetentionConfig = Field(
        default_factory=BackupRetentionConfig,
        description="Backup retention policy",
    )

    # Per-database configurations
    databases: List[BackupDatabaseConfig] = Field(
        default_factory=list,
        description="Per-database backup configurations",
    )

    # Compression
    compression: Literal["gzip", "bz2", "xz", "none"] = Field(
        default="gzip",
        description="Backup compression algorithm",
    )

    # Encryption (optional)
    encryption_key: Optional[str] = Field(
        default=None,
        description="Encryption key for backup files (GPG-compatible)",
        repr=False,
    )

    # Notifications
    notify_on_success: bool = Field(
        default=False,
        description="Send notification on successful backup",
    )

    notify_on_failure: bool = Field(
        default=True,
        description="Send notification on backup failure",
    )

    # Backup file naming
    filename_template: str = Field(
        default="{database}_{timestamp}_{env}",
        description="Backup filename template",
    )

    @field_validator("filename_template")
    @classmethod
    def validate_filename_template(cls, v: str) -> str:
        """Validate filename template has required placeholders."""
        required = ["{database}", "{timestamp}"]
        for placeholder in required:
            if placeholder not in v:
                raise ValueError(f"Filename template must include {placeholder}")
        return v

    def get_database_config(self, alias: str) -> Optional[BackupDatabaseConfig]:
        """Get configuration for specific database."""
        for db_config in self.databases:
            if db_config.alias == alias:
                return db_config
        return None

    def should_backup_database(self, alias: str) -> bool:
        """Check if database should be backed up."""
        if not self.enabled:
            return False
        db_config = self.get_database_config(alias)
        if db_config:
            return db_config.enabled
        return True  # Default: backup all databases

    def to_rq_schedule(self, database_alias: str = "default") -> Optional[Dict[str, Any]]:
        """
        Generate RQ schedule configuration for this backup.

        Returns None if scheduling is disabled or RQ is not available.
        """
        if not self.enabled or not self.schedule.enabled:
            return None

        db_config = self.get_database_config(database_alias)
        schedule = db_config.schedule_override if db_config and db_config.schedule_override else self.schedule

        cron = schedule.to_cron_expression()
        if not cron:
            return None

        return {
            "func": "extensions.apps.backup.tasks.run_scheduled_backup",
            "cron": cron,
            "queue": schedule.queue,
            "kwargs": {"database_alias": database_alias},
        }


# Export all models
__all__ = [
    "BackupConfig",
    "BackupDatabaseConfig",
    "BackupRetentionConfig",
    "BackupScheduleConfig",
    "BackupStorageConfig",
]
