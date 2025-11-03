"""
Payments v2.0 - Simplified Universal Payment System.

Features:
- NowPayments cryptocurrency provider (polling-based)
- ORM-based balance calculation
- Manual withdrawal approval
- Simplified currency model (token+network combined)

Configuration:
    from django_cfg.apps.business.payments.config import get_nowpayments_config
"""

default_app_config = 'django_cfg.apps.business.payments.apps.PaymentsConfig'
