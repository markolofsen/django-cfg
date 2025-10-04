"""
Maintenance app configuration.
"""

from django.apps import AppConfig


class MaintenanceConfig(AppConfig):
    """Configuration for the simplified maintenance app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_cfg.apps.maintenance'
    verbose_name = 'Maintenance Mode'
    
    def ready(self):
        """Initialize app when Django starts."""
        # No complex signals or initialization needed
        pass
