"""
Admin interfaces for Universal Payment System v2.0.

Unfold-powered admin with modern UI/UX and advanced functionality.
"""

from .currencies_admin import CurrencyAdmin, NetworkAdmin, ProviderCurrencyAdmin
from .payments_admin import UniversalPaymentAdmin
from .balance_admin import UserBalanceAdmin, TransactionAdmin
from .subscriptions_admin import SubscriptionAdmin, EndpointGroupAdmin, TariffAdmin, TariffEndpointGroupAdmin
from .api_keys_admin import APIKeyAdmin

__all__ = [
    # Currency admins
    'CurrencyAdmin',
    'NetworkAdmin', 
    'ProviderCurrencyAdmin',
    
    # Payment admins
    'UniversalPaymentAdmin',
    
    # Balance admins
    'UserBalanceAdmin',
    'TransactionAdmin',
    
    # Subscription admins
    'SubscriptionAdmin',
    'EndpointGroupAdmin',
    'TariffAdmin',
    'TariffEndpointGroupAdmin',
    
    # API Key admins
    'APIKeyAdmin',
]
