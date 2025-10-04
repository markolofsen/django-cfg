"""Django DRF Tailwind Theme app configuration."""

from django.apps import AppConfig


class DjangoDRFThemeConfig(AppConfig):
    """App configuration for Django DRF Tailwind Theme."""

    name = "django_cfg.modules.django_drf_theme"
    verbose_name = "Django DRF Tailwind Theme"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        """Initialize the app when Django starts."""
        pass
