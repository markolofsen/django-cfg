"""
Admin interfaces for universal payments.
"""

from .balance_admin import UserBalanceAdmin, TransactionAdmin
from .payments_admin import UniversalPaymentAdmin
from .subscriptions_admin import SubscriptionAdmin, EndpointGroupAdmin
from .api_keys_admin import APIKeyAdmin
from .currencies_admin import CurrencyAdmin, NetworkAdmin, ProviderCurrencyAdmin
from .tariffs_admin import TariffAdmin, TariffEndpointGroupAdmin

__all__ = [
    'UserBalanceAdmin',
    'TransactionAdmin',
    'UniversalPaymentAdmin',
    'SubscriptionAdmin',
    'EndpointGroupAdmin',
    'APIKeyAdmin',
    'CurrencyAdmin',
    'NetworkAdmin',
    'ProviderCurrencyAdmin',
    'TariffAdmin',
    'TariffEndpointGroupAdmin',
]
