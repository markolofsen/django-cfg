"""
Django app configuration for IPC/RPC module.

Provides RPC client and monitoring dashboard.
"""

from django.apps import AppConfig


class IPCConfig(AppConfig):
    """
    IPC/RPC application configuration.

    Provides:
    - RPC client for inter-service communication
    - Monitoring dashboard with real-time stats
    - DRF API endpoints for dashboard
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_cfg.apps.ipc'
    label = 'django_cfg_ipc'
    verbose_name = 'IPC/RPC System'

    def ready(self):
        """Initialize app when Django starts."""
        # Import monitor to ensure Redis connection is initialized
        from .services import monitor  # noqa: F401
