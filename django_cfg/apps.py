"""
Django Config Toolkit App Configuration

Provides Django app configuration for the toolkit.
"""

from django.apps import AppConfig


class DjangoConfigToolkitConfig(AppConfig):
    """Configuration for Django Config Toolkit app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_cfg'
    verbose_name = 'Django Config Toolkit'
    
    def ready(self):
        """Initialize the toolkit when Django app is ready."""
        # Import signals or perform initialization here if needed
        pass
