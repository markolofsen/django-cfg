from django.apps import AppConfig


class LeadsConfig(AppConfig):
    """Leads application configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_cfg.apps.leads"
    label = "django_cfg_leads"
    verbose_name = "Django CFG Leads"

    def ready(self):
        try:
            import django_cfg.apps.leads.signals  # noqa
        except ImportError:
            pass