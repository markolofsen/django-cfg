"""
Database Backup App Configuration.
"""

from django.apps import AppConfig


class DbBackupConfig(AppConfig):
    """Configuration for Database Backup application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_cfg.apps.system.db"
    label = "db_backup"
    verbose_name = "Database Backup"

    def ready(self):
        """
        Application initialization.

        Registers scheduled backup tasks if Django-RQ is enabled.
        """
        self._register_scheduled_tasks()

    def _register_scheduled_tasks(self):
        """Register backup tasks with Django-RQ scheduler if enabled."""
        try:
            from django_cfg.core.state.registry import get_current_config

            config = get_current_config()
            if not config:
                return

            # Check if backup is enabled
            backup_config = getattr(config, "backup", None)
            if not backup_config or not backup_config.enabled:
                return

            # Check if RQ is enabled for scheduled backups
            if not config.should_enable_rq():
                return

            # Schedule will be registered via Django-RQ settings
            # The actual registration happens in DjangoRQConfig.to_django_settings()

        except Exception:
            # Silently ignore if config not ready yet
            pass
