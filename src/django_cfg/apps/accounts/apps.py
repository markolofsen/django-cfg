"""
Accounts Application Configuration
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Accounts application configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_cfg.apps.accounts"
    label = "django_cfg_accounts"
    verbose_name = "Django CFG Accounts"

    def ready(self):
        """Initialize the accounts application."""
        # Import signal handlers
        import django_cfg.apps.accounts.signals  # noqa
