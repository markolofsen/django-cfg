"""Django AppConfig for tasks app."""
from django.apps import AppConfig


class TasksConfig(AppConfig):
    """Django app configuration for ReArq tasks."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_cfg.apps.tasks"
    verbose_name = "Background Tasks"

    def ready(self):
        """Initialize app when Django starts."""
        # Import services to ensure client is available
        from . import services  # noqa: F401
