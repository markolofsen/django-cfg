"""
Django app configuration for Centrifugo module.

Provides Centrifugo pub/sub client with ACK tracking.
"""

from django.apps import AppConfig


class CentrifugoConfig(AppConfig):
    """
    Centrifugo application configuration.

    Provides:
    - Async client for publishing messages to Centrifugo
    - ACK tracking for delivery confirmation
    - Logging of all publish operations
    - Migration-friendly API (mirrors legacy WebSocket solution patterns)
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_cfg.apps.centrifugo"
    label = "django_cfg_centrifugo"
    verbose_name = "Centrifugo WebSocket"

    def ready(self):
        """Initialize app when Django starts."""
        from django_cfg.modules.django_logging import get_logger

        logger = get_logger("centrifugo.apps")
        logger.info("Centrifugo app initialized")
