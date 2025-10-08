"""
Django Client AppConfig.

Initializes OpenAPI service with configuration from Django settings.
"""

from django.apps import AppConfig
from django.conf import settings


class DjangoClientConfig(AppConfig):
    """AppConfig for django_client."""

    name = 'django_cfg.modules.django_client'
    verbose_name = 'Django OpenAPI Client'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        """Initialize OpenAPI service on app startup."""
        # Import here to avoid AppRegistryNotReady
        from django_cfg.modules.django_client.core import get_openapi_service
        from django_cfg.core.state.registry import get_current_config

        # Get config from django-cfg
        django_config = get_current_config()
        if not django_config or not hasattr(django_config, 'openapi_client'):
            return

        config = django_config.openapi_client

        if config and config.enabled:
            # Initialize service with config
            service = get_openapi_service()
            service.set_config(config)
            print(f"✅ Django Client initialized with {len(config.groups)} groups")
