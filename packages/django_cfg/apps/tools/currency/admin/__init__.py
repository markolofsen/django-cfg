"""
Currency Admin

Export all admin classes.
"""

from django_cfg.apps.tools.currency.admin.currency_rate_admin import (
    CurrencyRateAdmin,
    currency_rate_admin_config,
)
from django_cfg.apps.tools.currency.admin.currency_admin import (
    CurrencyAdmin,
    currency_admin_config,
)

__all__ = [
    # CurrencyRate
    "CurrencyRateAdmin",
    "currency_rate_admin_config",
    # Currency
    "CurrencyAdmin",
    "currency_admin_config",
]
