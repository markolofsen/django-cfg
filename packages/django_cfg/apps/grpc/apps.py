"""
Django app configuration for gRPC integration.
"""

from django.apps import AppConfig


class GRPCAppConfig(AppConfig):
    """
    Django app config for gRPC integration.

    Provides:
    - gRPC server with Django ORM integration
    - JWT authentication
    - Request logging to database
    - Admin interface for monitoring
    - REST API for metrics
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_cfg.apps.grpc'
    verbose_name = 'gRPC Integration'

    def ready(self):
        """Called when Django starts."""
        # Import signal handlers if needed
        # from . import signals
        pass
