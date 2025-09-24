"""
Universal Payment Configuration.

Modular configuration system for the payments module.
"""

# Core configuration classes
from .settings import PaymentsSettings

# Import unified settings from models.payments
from django_cfg.models.payments import (
    SecuritySettings,
    RateLimitSettings,
    NotificationSettings,
    SubscriptionSettings
)

# Provider configurations - import from models.payments
from django_cfg.models.payments import (
    PaymentProviderConfig,
    NowPaymentsConfig,
    StripeConfig,
    CryptAPIConfig
)

# Local provider configs (additional to models.payments)
from .providers import CryptomusConfig

# Configuration module
from .module import PaymentsCfgModule

# Utility functions
from .utils import (
    get_payments_config,
    get_provider_config,
    is_payments_enabled
)

# Backwards compatibility exports
payments_config = PaymentsCfgModule()

__all__ = [
    # Core settings
    'PaymentsSettings',
    'SecuritySettings',
    'RateLimitSettings',
    'NotificationSettings',
    'SubscriptionSettings',
    
    # Provider configurations
    'PaymentProviderConfig',
    'NowPaymentsConfig',
    'StripeConfig',
    'CryptAPIConfig',
    'CryptomusConfig',
    
    # Configuration module
    'PaymentsCfgModule',
    'payments_config',
    
    # Utility functions
    'get_payments_config',
    'get_provider_config',
    'is_payments_enabled',
]
