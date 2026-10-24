from django.apps import AppConfig

from .__cfg__ import settings


class LeadsConfig(AppConfig):
    """Leads extension application configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "extensions.apps.leads"
    label = settings.full_app_label
    verbose_name = "Leads"

    def ready(self):
        try:
            from . import signals  # noqa
        except ImportError:
            pass
