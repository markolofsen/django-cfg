"""Currency app configuration."""

from django.apps import AppConfig


class CurrencyConfig(AppConfig):
    """Currency rates management app."""

    name = "django_cfg.apps.tools.currency"
    label = "cfg_currency"
    verbose_name = "Currency"
    default_auto_field = "django.db.models.BigAutoField"
