"""
AppConfig for Django-RQ integration with monitoring and API capabilities.

This app provides REST API endpoints for Django-RQ task queue monitoring,
management, and statistics. It wraps django-rq's functionality with modern
DRF ViewSets and unified django-cfg patterns.

Features:
- REST API for monitoring queues, workers, and jobs
- Prometheus metrics integration
- Enhanced monitoring interfaces
- Job management (view, requeue, delete)
- Integration with django-cfg ecosystem (Centrifugo, auth)
"""

from django.apps import AppConfig


class RQAppConfig(AppConfig):
    """
    AppConfig for Django-RQ monitoring and management application.

    Provides:
    - REST API endpoints for monitoring
    - Prometheus metrics export
    - Job and queue management
    - Worker statistics
    - Integration with django-cfg authentication

    Usage:
        Add to INSTALLED_APPS:
        INSTALLED_APPS = [
            ...
            'django_rq',  # Required: django-rq core
            'django_cfg.apps.rq',  # Django-CFG RQ monitoring
        ]

        Configure in django-cfg config:
        class MyConfig(BaseConfig):
            django_rq: DjangoRQConfig = DjangoRQConfig(
                enabled=True,
                queues={
                    'default': {
                        'host': 'localhost',
                        'port': 6379,
                        'db': 0,
                    }
                },
                prometheus_enabled=True,
            )
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_cfg.apps.rq'
    verbose_name = 'Django-CFG RQ Monitoring'
    label = 'django_cfg_rq'

    def ready(self):
        """
        Initialize the app when Django starts.

        Registers:
        - Admin interfaces (if not already registered)
        - Signal handlers for monitoring
        - Scheduled jobs from config
        """
        # Import admin to register custom admin classes
        try:
            from . import admin  # noqa: F401
        except ImportError:
            pass

        # Register scheduled jobs from config (runs once on startup)
        try:
            from .services import register_schedules_from_config
            register_schedules_from_config()
        except Exception as e:
            from django_cfg.modules.django_logging import get_logger
            logger = get_logger("rq.apps")
            logger.warning(f"Failed to register schedules: {e}")
