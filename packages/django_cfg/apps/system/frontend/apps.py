"""Django CFG Frontend App Configuration."""

from django.apps import AppConfig


class FrontendConfig(AppConfig):
    """Configuration for Django CFG Frontend app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_cfg.apps.system.frontend'
    verbose_name = 'Frontend Applications'

    def ready(self):
        """Initialize app when Django starts."""
        pass
