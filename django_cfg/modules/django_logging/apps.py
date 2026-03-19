"""django_logging AppConfig — wire D1 capture on startup."""

from django.apps import AppConfig


class DjangoLoggingAppConfig(AppConfig):
    name = "django_cfg.modules.django_logging"
    label = "django_logging"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        from .capture import connect_capture
        connect_capture()
