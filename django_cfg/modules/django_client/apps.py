"""
Django Client AppConfig.

Initializes OpenAPI service with configuration from Django settings.
"""

from django.apps import AppConfig


class DjangoClientConfig(AppConfig):
    """AppConfig for django_client."""

    name = 'django_cfg.modules.django_client'
    verbose_name = 'Django OpenAPI Client'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        """Initialize OpenAPI service on app startup."""
        # Import here to avoid AppRegistryNotReady
        from django_cfg.core.state.registry import get_current_config
        from django_cfg.modules.django_client.core import get_openapi_service

        # Get config from django-cfg
        django_config = get_current_config()
        if not django_config or not hasattr(django_config, 'openapi_client'):
            return

        config = django_config.openapi_client

        if config and config.enabled:
            # Add default 'cfg' group if not already present
            cfg_group_exists = any(g.name == 'cfg' for g in config.groups)
            if not cfg_group_exists:
                from django_cfg.apps.urls import get_default_cfg_group
                cfg_group = get_default_cfg_group()
                if cfg_group.apps:
                    config.groups.append(cfg_group)

            # Initialize service with config
            service = get_openapi_service()
            service.set_config(config)

            # Create urlconf modules for all groups (including auto-detected cfg_* groups).
            # We use _build_urlpatterns directly because get_group_apps() matches against
            # INSTALLED_APPS and misses auto-groups whose apps are not explicitly installed.
            import sys
            from types import ModuleType
            from django_cfg.modules.django_client.core.groups import GroupManager
            manager = GroupManager(config)
            for group in config.get_groups_with_defaults().values():
                if not group.apps:
                    continue
                module_name = f"_django_client_urlconf_{group.name}"
                try:
                    urlpatterns = manager._build_urlpatterns(group.name, group.apps)
                    module = ModuleType(module_name)
                    module.__file__ = f"<dynamic: {group.name}>"
                    module.urlpatterns = urlpatterns
                    sys.modules[module_name] = module
                except Exception:
                    pass

            # Update urlpatterns after service is configured
            from django_cfg.modules.django_client import urls
            urls.urlpatterns.clear()
            urls.urlpatterns.extend(urls.get_openapi_urls())
