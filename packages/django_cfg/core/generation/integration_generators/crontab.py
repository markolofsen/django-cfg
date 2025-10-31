"""
Crontab settings generator for django-cfg.

Generates django-crontab settings and handles INSTALLED_APPS integration.
"""

from typing import TYPE_CHECKING, Any, Dict

from django_cfg.modules.django_logging import logger

if TYPE_CHECKING:
    from django_cfg.models.django.crontab import CrontabConfig


class CrontabSettingsGenerator:
    """
    Generates crontab scheduling settings for django-crontab.

    Automatically:
    - Generates CRONJOBS configuration
    - Adds django_crontab to INSTALLED_APPS if enabled
    - Configures lock files and command prefixes
    """

    def __init__(self, config: "CrontabConfig"):
        """
        Initialize with crontab configuration.

        Args:
            config: CrontabConfig instance
        """
        self.config = config

    def generate(self) -> Dict[str, Any]:
        """
        Generate crontab settings.

        Returns:
            Dictionary with crontab configuration
        """
        if not self.config or not self.config.enabled:
            return {}

        settings = self.config.to_django_settings()

        # Log configuration
        enabled_jobs = self.config.get_enabled_jobs()
        if enabled_jobs:
            logger.info(
                f"✓ Configured {len(enabled_jobs)} crontab job(s) "
                f"[django-crontab integration]"
            )

            # Log individual jobs in debug mode
            for job in enabled_jobs:
                logger.debug(
                    f"  - {job.name}: {job.schedule} → "
                    f"{job.command if job.job_type == 'command' else job.callable_path}"
                )

        return settings


__all__ = ["CrontabSettingsGenerator"]
