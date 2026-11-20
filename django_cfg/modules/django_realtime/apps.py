"""Installed when `DjangoConfig.realtime.enabled`: imports every app's `realtime.py` and provides `manage.py realtime`."""

from django.apps import AppConfig


class DjangoRealtimeAppConfig(AppConfig):
    name = "django_cfg.modules.django_realtime"
    label = "django_cfg_realtime"
    verbose_name = "Realtime"
    default = True

    def ready(self) -> None:
        from . import signals
        from .registry import registry

        registry.ensure_discovered()
        signals.connect()
