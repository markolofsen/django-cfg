"""
Django app configuration for universal payments.
"""

from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    """Universal payments app configuration."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_cfg.apps.payments'
    label = 'django_cfg_payments'
    verbose_name = 'Universal Payments'
    
    def ready(self):
        """Called when the app is ready."""
        # Import signals if any
        try:
            from . import signals  # noqa
        except ImportError:
            pass
