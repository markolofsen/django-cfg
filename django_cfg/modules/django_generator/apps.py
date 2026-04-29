"""AppConfig for django_generator."""

from django.apps import AppConfig


class DjangoGeneratorConfig(AppConfig):
    name = "django_cfg.modules.django_generator"
    label = "django_generator"
    verbose_name = "Django OpenAPI Generator"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        import sys
        from types import ModuleType

        from django_cfg.core.state.registry import get_current_config
        from .openapi.groups.manager import GroupManager
        from .openapi.service import get_openapi_service

        django_config = get_current_config()
        if not django_config or not hasattr(django_config, "openapi_client"):
            return

        config = django_config.openapi_client
        if not (config and config.enabled):
            return

        service = get_openapi_service()
        service.set_config(config)

        # Pre-register synthetic urlconf modules for every group.
        #
        # `urls.get_openapi_urls()` builds `SpectacularAPIView(urlconf="_django_generator_urlconf_<group>")`
        # — passed as a STRING, so drf-spectacular resolves it via
        # `importlib.import_module(name)` at request time. If we don't
        # populate `sys.modules[name]` here, every per-group `/schema/`
        # request fails with `ModuleNotFoundError`. Lazy creation in
        # `GroupManager.create_urlconf_module` is only used by the CLI
        # generator path; runtime requests never trigger it.
        manager = GroupManager(config)
        for group in config.get_groups_with_defaults().values():
            if not group.apps:
                continue
            module_name = f"_django_generator_urlconf_{group.name}"
            try:
                urlpatterns = manager._build_urlpatterns(group.name, group.apps)
            except Exception:
                # A broken group should not crash app startup — skip and
                # let the per-group request fail loudly instead.
                continue
            module = ModuleType(module_name)
            module.__file__ = f"<dynamic: {group.name}>"
            module.urlpatterns = urlpatterns  # type: ignore[attr-defined]
            sys.modules[module_name] = module
