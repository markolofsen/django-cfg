"""Django app configuration for the ready chat."""

from django.apps import AppConfig


class ChatAppConfig(AppConfig):
    name = "django_cfg.apps.tools.chat"
    label = "cfg_chat"
    verbose_name = "Assistant chat"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        from .kinds import register_default_kind

        register_default_kind()
