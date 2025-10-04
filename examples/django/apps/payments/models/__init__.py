"""
Universal Payment System v2.0 - Models Package.

Simplified models focused on NowPayments with extensible architecture.
All models follow the data typing requirements: Django ORM for database layer.
"""

# Base models
from .base import UUIDTimestampedModel

# Currency models
from .currencies import Currency, Network, ProviderCurrency

# Payment models  
from .payments import UniversalPayment

# Balance models
from .balance import UserBalance, Transaction

# Subscription models
from .subscriptions import Subscription, EndpointGroup

# Tariff models
from .tariffs import Tariff, TariffEndpointGroup

# API Keys
from .api_keys import APIKey

# Export TextChoices for external use
PaymentStatus = UniversalPayment.PaymentStatus
PaymentProvider = UniversalPayment.PaymentProvider
CurrencyType = Currency.CurrencyType
TransactionType = Transaction.TransactionType
SubscriptionStatus = Subscription.SubscriptionStatus
SubscriptionTier = Subscription.SubscriptionTier

__all__ = [
    # Base
    'UUIDTimestampedModel',
    
    # Currencies
    'Currency',
    'Network',
    'ProviderCurrency',
    
    # Core Models
    'UniversalPayment',
    'UserBalance',
    'Transaction', 
    'Subscription',
    'EndpointGroup',
    'Tariff',
    'TariffEndpointGroup',
    'APIKey',
    
    # TextChoices
    'PaymentStatus',
    'PaymentProvider',
    'CurrencyType',
    'TransactionType',
    'SubscriptionStatus',
    'SubscriptionTier',
]
