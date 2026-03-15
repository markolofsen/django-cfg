"""
Dashboard App Configuration
"""

from django.apps import AppConfig


class DashboardConfig(AppConfig):
    """Configuration for Dashboard application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_cfg.apps.api.dashboard'
    label = 'dashboard'
    verbose_name = 'Dashboard'

    def ready(self):
        """
        Application initialization.

        Called when Django starts. Import signals or perform
        other initialization tasks here.
        """
        pass
