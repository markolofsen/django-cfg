"""
Payment admin interfaces for Payments v2.0.

Modern, clean admin interfaces with Unfold UI and no HTML duplication.

Features:
- Payment management with NowPayments integration
- Balance and transaction tracking
- Manual withdrawal approval workflow
- Currency management (token+network model)
"""

from django.contrib import admin

# Import all admin classes (auto-registered via @admin.register decorator)
from .balance_admin import TransactionAdmin, UserBalanceAdmin
from .currency_admin import CurrencyAdmin
from .payment_admin import PaymentAdmin
from .withdrawal_admin import WithdrawalRequestAdmin

# All models are registered in their respective admin files using @admin.register
# This provides:
# - Clean separation of concerns
# - Unfold UI integration
# - Type-safe configurations
# - Performance optimizations
# - No HTML duplication

__all__ = [
    'PaymentAdmin',
    'UserBalanceAdmin',
    'TransactionAdmin',
    'CurrencyAdmin',
    'WithdrawalRequestAdmin',
]
