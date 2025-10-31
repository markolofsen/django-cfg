"""
Django app configuration for django_admin module.

This makes django_admin a proper Django app so templates are automatically discovered.
"""
from django.apps import AppConfig


class DjangoAdminConfig(AppConfig):
    """Configuration for django_admin module."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_cfg.modules.django_admin"
    label = "django_cfg_admin"
    verbose_name = "Django Admin (django-cfg)"

    def ready(self):
        """Called when Django is ready."""
        pass
