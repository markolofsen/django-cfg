"""
Database Backup Tasks for Django-RQ.

These tasks are automatically scheduled if:
1. BackupConfig.enabled = True
2. BackupConfig.schedule.enabled = True
3. Django-RQ is enabled (config.should_enable_rq() = True)

If Django-RQ is not enabled, use management commands for manual backups:
    python manage.py db_backup
    python manage.py db_restore <backup_id>
"""

import logging

logger = logging.getLogger(__name__)


def run_scheduled_backup(database_alias: str = "default"):
    """
    RQ task for scheduled database backup.

    This task is registered automatically when:
    - BackupConfig.enabled = True
    - BackupConfig.schedule.enabled = True
    - Django-RQ is enabled

    Args:
        database_alias: Django database alias to backup
    """
    from .services import BackupService

    logger.info(f"Starting scheduled backup for database: {database_alias}")

    try:
        service = BackupService()
        record = service.create_backup(
            database_alias=database_alias,
            is_scheduled=True,
            is_manual=False,
        )

        if record.status == "completed":
            logger.info(
                f"Scheduled backup completed: {record.filename} "
                f"({record.file_size_human}, {record.duration_human})"
            )
        else:
            logger.error(f"Scheduled backup failed: {record.error_message}")

        return {
            "status": record.status,
            "filename": record.filename,
            "file_size": record.file_size,
            "duration": record.duration_seconds,
            "error": record.error_message if record.status == "failed" else None,
        }

    except Exception as e:
        logger.exception(f"Scheduled backup failed for {database_alias}")
        raise


def run_backup_cleanup():
    """
    RQ task for cleaning up old backups according to retention policy.

    This task can be scheduled to run periodically (e.g., daily).
    """
    from .services import BackupService

    logger.info("Starting backup cleanup")

    try:
        service = BackupService()
        service.cleanup_old_backups()
        logger.info("Backup cleanup completed")

    except Exception as e:
        logger.exception("Backup cleanup failed")
        raise


def run_all_databases_backup():
    """
    RQ task to backup all configured databases.

    Iterates through all databases in Django settings and creates backups
    for those enabled in BackupConfig.
    """
    from django.conf import settings

    from .services import BackupService

    logger.info("Starting backup for all databases")

    service = BackupService()
    results = []

    for alias in settings.DATABASES.keys():
        if service.config and not service.config.should_backup_database(alias):
            logger.info(f"Skipping database {alias} (disabled in config)")
            continue

        try:
            record = service.create_backup(
                database_alias=alias,
                is_scheduled=True,
                is_manual=False,
            )
            results.append({
                "database": alias,
                "status": record.status,
                "filename": record.filename,
            })

        except Exception as e:
            logger.error(f"Backup failed for {alias}: {e}")
            results.append({
                "database": alias,
                "status": "failed",
                "error": str(e),
            })

    logger.info(f"Completed backup for {len(results)} databases")
    return results


def get_rq_schedules():
    """
    Get RQ schedule configurations for backup tasks.

    Called by Django-RQ configuration to register scheduled tasks.

    Returns:
        List of RQScheduleConfig-compatible dictionaries
    """
    try:
        from django_cfg.core.state.registry import get_current_config

        config = get_current_config()
        if not config:
            return []

        backup_config = getattr(config, "backup", None)
        if not backup_config or not backup_config.enabled:
            return []

        if not backup_config.schedule.enabled:
            return []

        schedules = []

        # Main backup schedule
        cron = backup_config.schedule.to_cron_expression()
        if cron:
            schedules.append({
                "func": "django_cfg.apps.system.db.tasks.run_all_databases_backup",
                "cron": cron,
                "queue": backup_config.schedule.queue,
            })

        # Cleanup schedule (daily at 3 AM)
        if backup_config.retention.enabled:
            schedules.append({
                "func": "django_cfg.apps.system.db.tasks.run_backup_cleanup",
                "cron": "0 3 * * *",
                "queue": backup_config.schedule.queue,
            })

        return schedules

    except Exception:
        return []
