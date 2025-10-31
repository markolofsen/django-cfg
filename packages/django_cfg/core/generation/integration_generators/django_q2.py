"""
Django-Q2 settings generator for django-cfg.

Generates django-q2 settings and handles INSTALLED_APPS integration.
"""

from typing import TYPE_CHECKING, Any, Dict, Optional

from django_cfg.modules.django_logging import logger

if TYPE_CHECKING:
    from django_cfg.models.django.django_q import DjangoQ2Config


class DjangoQ2SettingsGenerator:
    """
    Generates task scheduling settings for django-q2.

    Automatically:
    - Generates Q_CLUSTER configuration
    - Adds django_q to INSTALLED_APPS if enabled
    - Configures broker, workers, and task settings
    - Provides schedule management via Django ORM

    Django-Q2 vs django-crontab:
    - No need to run 'crontab add' - schedules in database
    - Built-in admin interface for monitoring
    - Support for both cron and interval scheduling
    - Task retries and hooks
    - Async task support
    """

    def __init__(self, config: "DjangoQ2Config", parent_config: Optional[Any] = None):
        """
        Initialize with Django-Q2 configuration.

        Args:
            config: DjangoQ2Config instance
            parent_config: Optional parent DjangoConfig for accessing redis_url
        """
        self.config = config
        self.parent_config = parent_config

    def generate(self) -> Dict[str, Any]:
        """
        Generate Django-Q2 settings.

        Returns:
            Dictionary with Q_CLUSTER configuration
        """
        if not self.config or not self.config.enabled:
            return {}

        settings = self.config.to_django_settings(parent_config=self.parent_config)

        # Log configuration
        logger.info(
            f"✓ Configured Django-Q2 task queue "
            f"[broker: {self.config.broker_class}, workers: {self.config.workers}]"
        )

        enabled_schedules = self.config.get_enabled_schedules()
        if enabled_schedules:
            logger.info(
                f"✓ Found {len(enabled_schedules)} scheduled task(s) "
                f"[use admin or management commands to create schedules]"
            )

            # Log individual schedules in debug mode
            for schedule in enabled_schedules:
                logger.debug(
                    f"  - {schedule.name}: {schedule.schedule_type} → "
                    f"{schedule.command if schedule.command else schedule.func}"
                )

            logger.info(
                "📝 To create schedules: python manage.py qcluster "
                "or use Django admin at /admin/django_q/schedule/"
            )

        return settings

    def generate_schedule_creation_code(self) -> str:
        """
        Generate Python code to create schedules programmatically.

        Returns:
            Python code string for creating schedules

        Example:
            ```python
            code = generator.generate_schedule_creation_code()
            # Use in management command or startup script
            ```
        """
        if not self.config or not self.config.enabled:
            return ""

        enabled_schedules = self.config.get_enabled_schedules()
        if not enabled_schedules:
            return ""

        lines = [
            "# Auto-generated Django-Q2 schedule creation",
            "from django_q.models import Schedule",
            "",
            "# Create or update schedules",
        ]

        for schedule in enabled_schedules:
            schedule_dict = schedule.to_django_q_format()

            lines.append("")
            lines.append(f"# {schedule.name}")
            lines.append("Schedule.objects.update_or_create(")
            lines.append(f"    name='{schedule.name}',")
            lines.append("    defaults={")

            for key, value in schedule_dict.items():
                if key == "name":
                    continue
                if isinstance(value, str):
                    lines.append(f"        '{key}': '{value}',")
                else:
                    lines.append(f"        '{key}': {value},")

            lines.append("    }")
            lines.append(")")

        return "\n".join(lines)


__all__ = ["DjangoQ2SettingsGenerator"]
