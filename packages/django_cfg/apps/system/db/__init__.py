"""
Database Backup Application.

Provides database backup and restore functionality with:
- Multi-database support (PostgreSQL, MySQL, SQLite)
- Scheduled backups via Django-RQ (if enabled)
- Manual backups via management commands
- Storage backends (local, S3-compatible)
- Backup retention policies
- Admin interface and API

Usage:
    # Enable in DjangoConfig
    backup: BackupConfig = BackupConfig(
        enabled=True,
        storage=BackupStorageConfig(backend="local"),
        schedule=BackupScheduleConfig(cron="0 2 * * *"),
    )
"""

default_app_config = "django_cfg.apps.system.db.apps.DbBackupConfig"
