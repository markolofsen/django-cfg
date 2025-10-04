"""
Django CFG Tasks App Configuration
"""

from django.apps import AppConfig


class TasksConfig(AppConfig):
    """Configuration for Django CFG Tasks app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_cfg.apps.tasks'
    verbose_name = 'Background Tasks'
    
    def ready(self):
        """Initialize app when Django starts."""
        pass
