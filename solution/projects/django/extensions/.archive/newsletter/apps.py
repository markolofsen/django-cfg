"""
Newsletter Application Configuration
"""

from django.apps import AppConfig

from .__cfg__ import settings


class NewsletterConfig(AppConfig):
    """Newsletter application configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "extensions.apps.newsletter"
    label = settings.full_app_label  # Auto: cfg__newsletter
    verbose_name = "Django CFG Newsletter"

    def ready(self):
        """Initialize the newsletter application."""
        try:
            from . import signals  # noqa
        except ImportError:
            pass
