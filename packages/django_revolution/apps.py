"""
Django Revolution App Configuration

Django app configuration for the Django Revolution package.
"""

from django.apps import AppConfig


class DjangoRevolutionConfig(AppConfig):
    """Django app configuration for Django Revolution."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_revolution"
    verbose_name = "Django Revolution"
