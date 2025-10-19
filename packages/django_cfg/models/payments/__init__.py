"""
Simplified payment configuration models for Payments v2.0.

Only supports NowPayments provider.
"""

from .config import NowPaymentsConfig, PaymentsConfig

__all__ = [
    "PaymentsConfig",
    "NowPaymentsConfig",
]
