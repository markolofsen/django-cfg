"""
Universal payments models package.

Django ORM models for the universal payments system.
"""

# Base models
from .base import TimestampedModel

# Currency models
from .currencies import Currency, Network, ProviderCurrency

# Payment models  
from .payments import UniversalPayment

# Balance models
from .balance import UserBalance, Transaction

# Subscription models
from .subscriptions import EndpointGroup, Subscription

# Tariff models
from .tariffs import Tariff, TariffEndpointGroup

# API Keys
from .api_keys import APIKey

# Event sourcing
from .events import PaymentEvent

# TextChoices classes for external use (accessing inner classes)
CurrencyType = Currency.CurrencyType
PaymentStatus = UniversalPayment.PaymentStatus
PaymentProvider = UniversalPayment.PaymentProvider
TransactionType = Transaction.TransactionType
SubscriptionStatus = Subscription.SubscriptionStatus
SubscriptionTier = Subscription.SubscriptionTier
EventType = PaymentEvent.EventType

__all__ = [
    # Base
    'TimestampedModel',
    
    # Currencies
    'Currency',
    'Network',
    'ProviderCurrency',
    
    # Models
    'UniversalPayment',
    'UserBalance',
    'Transaction', 
    'EndpointGroup',
    'Subscription',
    'Tariff',
    'TariffEndpointGroup',
    'APIKey',
    'PaymentEvent',
    
    # TextChoices
    'CurrencyType',
    'PaymentStatus',
    'PaymentProvider', 
    'TransactionType',
    'SubscriptionStatus',
    'SubscriptionTier',
    'EventType',
]