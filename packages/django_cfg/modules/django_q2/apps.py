"""
AppConfig for Django-Q2 module with automatic schedule synchronization.
"""
import logging
from django.apps import AppConfig
from django.db.models.signals import post_migrate

logger = logging.getLogger(__name__)


def sync_schedules_after_migrate(sender, **kwargs):
    """
    Automatically sync Django-Q2 schedules after migrations.

    This ensures schedules are always up-to-date after deployment.
    Runs only once per migration cycle, safe from race conditions.
    """
    # Only run for the django_cfg_django_q2 app itself
    if sender.name != 'django_cfg.modules.django_q2':
        return

    # Import here to avoid circular imports and ensure Django is ready
    try:
        from django_q.models import Schedule
        from django_cfg.core.config import get_current_config
    except ImportError as e:
        logger.warning(f"Could not import Django-Q2 dependencies: {e}")
        return

    config = get_current_config()

    if not config or not hasattr(config, 'django_q2') or not config.django_q2 or not config.django_q2.enabled:
        logger.debug("Django-Q2 not enabled, skipping schedule sync")
        return

    enabled_schedules = config.django_q2.get_enabled_schedules()

    if not enabled_schedules:
        logger.debug("No Django-Q2 schedules found in config")
        return

    logger.info(f"Syncing {len(enabled_schedules)} Django-Q2 schedule(s)...")

    created = 0
    updated = 0

    for schedule_config in enabled_schedules:
        schedule_dict = schedule_config.to_django_q_format()
        name = schedule_dict['name']

        try:
            schedule, created_flag = Schedule.objects.update_or_create(
                name=name,
                defaults=schedule_dict
            )

            if created_flag:
                created += 1
                logger.info(f"  ✓ Created schedule: {name}")
            else:
                updated += 1
                logger.debug(f"  ✓ Updated schedule: {name}")

        except Exception as e:
            logger.error(f"  ✗ Failed to sync schedule '{name}': {e}")

    logger.info(f"✅ Django-Q2 schedules synced: {created} created, {updated} updated")


class DjangoQ2ModuleConfig(AppConfig):
    """
    AppConfig for Django-Q2 module.

    Automatically syncs schedules from config to database after migrations.
    This eliminates the need for manual `sync_django_q_schedules` command.

    Features:
    - Automatic schedule sync after migrations
    - Safe from race conditions (runs only once)
    - Logs all sync operations
    - Gracefully handles missing dependencies

    Usage:
        Add to INSTALLED_APPS:
        INSTALLED_APPS = [
            ...
            'django_cfg.modules.django_q2',  # Auto-syncs schedules
        ]
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_cfg.modules.django_q2'
    verbose_name = 'Django-CFG Django-Q2 Module'

    def ready(self):
        """
        Connect post_migrate signal to automatically sync schedules.

        This runs after all migrations are complete, ensuring:
        1. Database tables exist
        2. Config is loaded
        3. Schedules are synced only once per migration cycle
        """
        # Connect the signal
        post_migrate.connect(sync_schedules_after_migrate, sender=self)

        logger.debug(f"{self.verbose_name} initialized - auto-sync enabled")
