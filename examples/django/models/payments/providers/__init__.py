"""
Payment provider configurations.

Provides type-safe configuration for payment providers:
- BaseProviderConfig: Base class for all providers
- NowPaymentsProviderConfig: NowPayments provider
"""

from .base import BaseProviderConfig
from .nowpayments import NowPaymentsProviderConfig

__all__ = [
    "BaseProviderConfig",
    "NowPaymentsProviderConfig",
]
