"""Django app configuration for TOTP two-factor authentication."""

from django.apps import AppConfig


class TOTPConfig(AppConfig):
    """Configuration for the TOTP 2FA application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_cfg.apps.system.totp"
    label = "django_cfg_totp"
    verbose_name = "Two-Factor Authentication"

    def ready(self) -> None:
        """Initialize app when Django starts."""
        # Import signals to register handlers
        try:
            from . import signals  # noqa: F401
        except ImportError:
            pass
