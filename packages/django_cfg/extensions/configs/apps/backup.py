"""
Base settings for backup extension.

Provides database backup and restore functionality.
"""

from typing import Any, List, Literal, Optional

from pydantic import Field

from django_cfg.models.infrastructure.backup import (
    BackupDatabaseConfig,
    BackupRetentionConfig,
    BackupScheduleConfig,
    BackupStorageConfig,
)
from django_cfg.modules.django_admin.icons import Icons

from .base import BaseExtensionSettings, NavigationItem, NavigationSection


class BaseBackupSettings(BaseExtensionSettings):
    """
    Base settings for backup extension.

    Features:
    - Multi-database support (PostgreSQL, MySQL, SQLite)
    - Scheduled backups via Django-RQ
    - Storage backends (local, S3-compatible)
    - Backup retention policies
    - Admin interface and API

    All backup configuration is now in __cfg__.py, not DjangoConfig.
    """

    # === Manifest defaults ===
    name: str = "backup"
    version: str = "2.0.0"
    description: str = "Database backup and restore with multi-database support"
    author: str = "DjangoCFG Team"
    min_djangocfg_version: str = "1.5.0"
    django_app_label: str = "backup"
    url_prefix: str = "backup"
    url_namespace: str = "backup"

    # === Backup Configuration ===
    # These fields replace DjangoConfig.backup

    enabled: bool = Field(
        default=True,
        description="Enable database backup module"
    )

    storage: BackupStorageConfig = Field(
        default_factory=BackupStorageConfig,
        description="Backup storage configuration"
    )

    schedule: BackupScheduleConfig = Field(
        default_factory=BackupScheduleConfig,
        description="Backup schedule configuration"
    )

    retention: BackupRetentionConfig = Field(
        default_factory=BackupRetentionConfig,
        description="Backup retention policy"
    )

    databases: List[BackupDatabaseConfig] = Field(
        default_factory=list,
        description="Per-database backup configurations"
    )

    compression: Literal["gzip", "bz2", "xz", "none"] = Field(
        default="gzip",
        description="Backup compression algorithm"
    )

    encryption_key: Optional[str] = Field(
        default=None,
        description="Encryption key for backup files",
        repr=False
    )

    notify_on_success: bool = Field(
        default=False,
        description="Send notification on successful backup"
    )

    notify_on_failure: bool = Field(
        default=True,
        description="Send notification on backup failure"
    )

    filename_template: str = Field(
        default="{database}_{timestamp}_{env}",
        description="Backup filename template"
    )

    # === Admin Navigation ===
    navigation: NavigationSection = Field(
        default_factory=lambda: NavigationSection(
            title="Database Backup",
            icon=Icons.BACKUP,
            collapsible=True,
            items=[
                NavigationItem(
                    title="Backups",
                    icon=Icons.BACKUP,
                    app="backup",
                    model="backuprecord",
                ),
                NavigationItem(
                    title="Restores",
                    icon=Icons.RESTORE,
                    app="backup",
                    model="restorerecord",
                ),
            ],
        ),
    )

    def get_rq_schedules(self) -> list[Any]:
        """
        Generate RQ schedules for backup tasks.

        Uses settings from this extension config directly.
        """
        from django_cfg.models.django.django_rq import RQScheduleConfig

        schedules: list[RQScheduleConfig] = []

        if not self.enabled or not self.schedule.enabled:
            return schedules

        # Main backup schedule
        cron = self.schedule.to_cron_expression()
        if cron:
            schedules.append(
                RQScheduleConfig(
                    func="extensions.apps.backup.tasks.run_all_databases_backup",
                    cron=cron,
                    queue=self.schedule.queue,
                    description="Database Backup (scheduled)",
                )
            )

        # Cleanup schedule (daily at 3 AM) if retention enabled
        if self.retention.enabled:
            schedules.append(
                RQScheduleConfig(
                    func="extensions.apps.backup.tasks.run_backup_cleanup",
                    cron="0 3 * * *",
                    queue=self.schedule.queue,
                    description="Database Backup Cleanup (daily)",
                )
            )

        return schedules

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
