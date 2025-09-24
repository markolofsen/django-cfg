"""
Django app configuration for Django Agents.
"""

from django.apps import AppConfig


class AgentsConfig(AppConfig):
    """Django app configuration for Django Agents."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_cfg.apps.agents'
    label = 'django_cfg_agents'
    verbose_name = 'Django Agents'
    
    def ready(self):
        """Initialize app when Django starts."""
        # Import signal handlers
        try:
            from . import signals  # noqa
        except ImportError:
            pass
        
        # Initialize orchestrator registry
        try:
            from .integration.registry import initialize_registry
            initialize_registry()
        except ImportError:
            pass
