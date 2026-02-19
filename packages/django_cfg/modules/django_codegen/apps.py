"""
Django Codegen AppConfig.
"""

from django.apps import AppConfig


class DjangoCodegenConfig(AppConfig):
    """AppConfig for django_codegen."""

    name = "django_cfg.modules.django_codegen"
    verbose_name = "Django Codegen"
    default_auto_field = "django.db.models.BigAutoField"
