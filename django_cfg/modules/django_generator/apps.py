"""AppConfig for django_generator."""

from django.apps import AppConfig


class DjangoGeneratorConfig(AppConfig):
    name = "django_cfg.modules.django_generator"
    label = "django_generator"
    verbose_name = "Django OpenAPI Generator"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        from django_cfg.core.state.registry import get_current_config
        from .openapi.service import get_openapi_service

        django_config = get_current_config()
        if not django_config or not hasattr(django_config, "openapi_client"):
            return

        config = django_config.openapi_client
        if config and config.enabled:
            service = get_openapi_service()
            service.set_config(config)
