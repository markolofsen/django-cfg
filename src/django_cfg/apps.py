"""
Django app configuration for django_cfg.
"""

from django.apps import AppConfig


class DjangoCfgConfig(AppConfig):
    """Django app configuration for django_cfg."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_cfg'
    verbose_name = 'Django Configuration Framework'
    
    def ready(self):
        """Initialize django_cfg when Django starts."""
        pass
