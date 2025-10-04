"""
Mailer Application Configuration
"""

from django.apps import AppConfig


class NewsletterConfig(AppConfig):
    """Newsletter application configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_cfg.apps.newsletter"
    label = "django_cfg_newsletter"
    verbose_name = "Django CFG Newsletter"

    def ready(self):
        """Initialize the newsletter application."""
        # Import signal handlers
        try:
            import django_cfg.apps.newsletter.signals  # noqa
        except ImportError:
            pass
