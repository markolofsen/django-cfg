"""
Frontend Monitor Application Configuration.
"""

from django.apps import AppConfig


class FrontendMonitorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_cfg.apps.system.frontend_monitor"
    label = "django_cfg_frontend_monitor"
    verbose_name = "Frontend Monitor"

    def ready(self):
        import django_cfg.apps.system.frontend_monitor.signals  # noqa
