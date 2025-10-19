"""
Payments v2.0 - Simplified payment system.

Features:
- Deposits via NowPayments (crypto)
- Manual withdrawals (admin approval)
- ORM-based balance calculation
- No webhooks, no API keys, no subscriptions
"""

from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_cfg.apps.payments'
    verbose_name = 'Payments v2.0'
    label = 'payments'

    def ready(self):
        """Initialize app."""
        # Import signals if needed in future
        pass
