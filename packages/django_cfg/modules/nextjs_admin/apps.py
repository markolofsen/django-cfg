"""Django app configuration for Next.js Admin module."""

from django.apps import AppConfig


class NextJsAdminConfig(AppConfig):
    """App config for Next.js Admin integration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_cfg.modules.nextjs_admin"
    label = "nextjs_admin"
    verbose_name = "Next.js Admin"
