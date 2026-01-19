"""
AppConfig for Django Cleanup module.

Automatically registers cleanup signals for all models with file fields
when the app is ready.
"""

import logging

from django.apps import AppConfig, apps
from django.db.models.fields.files import FileField

logger = logging.getLogger(__name__)


class DjangoCleanupConfig(AppConfig):
    """AppConfig for automatic file cleanup registration."""

    name = "django_cfg.modules.django_cleanup"
    verbose_name = "Django Cleanup"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        """Register cleanup signals for all models with file fields."""
        from .config import get_config
        from .signals import connect_signals_for_model

        config = get_config()

        if not config.auto_cleanup:
            logger.debug("Auto cleanup is disabled, skipping signal registration")
            return

        # Get all models and register signals
        registered_count = 0

        for model in apps.get_models():
            # Check if model has file fields
            has_file_field = any(
                isinstance(field, FileField) for field in model._meta.get_fields()
            )

            if has_file_field:
                connect_signals_for_model(model)
                registered_count += 1

        if registered_count > 0:
            logger.debug(f"Registered file cleanup for {registered_count} models")
