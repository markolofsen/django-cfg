"""
Trading app configuration.
"""

from django.apps import AppConfig


class TradingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.trading'
    verbose_name = 'Trading'

    def ready(self):
        # Import signals
        try:
            import apps.trading.signals  # noqa
        except ImportError:
            pass
