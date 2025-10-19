"""
Custom admin filters for Payments v2.0.

Simplified filters for NowPayments-only system.
"""

from datetime import timedelta
from typing import List, Tuple

from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class PaymentStatusFilter(admin.SimpleListFilter):
    """Enhanced payment status filter with groupings."""

    title = _('Payment Status')
    parameter_name = 'status'

    def lookups(self, request, model_admin) -> List[Tuple[str, str]]:
        return [
            ('pending', _('⏳ Pending')),
            ('confirming', _('🔄 Confirming')),
            ('confirmed', _('✅ Confirmed')),
            ('completed', _('✅ Completed')),
            ('partially_paid', _('⚠️ Partially Paid')),
            ('failed', _('❌ Failed')),
            ('cancelled', _('🚫 Cancelled')),
            ('expired', _('⌛ Expired')),
            ('active', _('🟢 Active (Pending/Confirming/Confirmed)')),
            ('finished', _('🏁 Finished (Completed/Failed/Cancelled/Expired)')),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(
                status__in=['pending', 'confirming', 'confirmed', 'partially_paid']
            )
        elif self.value() == 'finished':
            return queryset.filter(
                status__in=['completed', 'failed', 'cancelled', 'expired']
            )
        elif self.value():
            return queryset.filter(status=self.value())
        return queryset


class PaymentAmountFilter(admin.SimpleListFilter):
    """Filter payments by USD amount ranges."""

    title = _('Amount (USD)')
    parameter_name = 'amount_range'

    def lookups(self, request, model_admin) -> List[Tuple[str, str]]:
        return [
            ('small', _('💵 Small ($1 - $10)')),
            ('medium', _('💰 Medium ($10 - $100)')),
            ('large', _('💰 Large ($100 - $1,000)')),
            ('huge', _('💎 Huge ($1,000+)')),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'small':
            return queryset.filter(amount_usd__gte=1, amount_usd__lt=10)
        elif self.value() == 'medium':
            return queryset.filter(amount_usd__gte=10, amount_usd__lt=100)
        elif self.value() == 'large':
            return queryset.filter(amount_usd__gte=100, amount_usd__lt=1000)
        elif self.value() == 'huge':
            return queryset.filter(amount_usd__gte=1000)
        return queryset


class RecentActivityFilter(admin.SimpleListFilter):
    """Filter by recent activity timeframes."""

    title = _('Recent Activity')
    parameter_name = 'recent_activity'

    def lookups(self, request, model_admin) -> List[Tuple[str, str]]:
        return [
            ('1h', _('🕐 Last Hour')),
            ('24h', _('📅 Last 24 Hours')),
            ('7d', _('📅 Last 7 Days')),
            ('30d', _('📅 Last 30 Days')),
            ('today', _('📅 Today')),
            ('yesterday', _('📅 Yesterday')),
        ]

    def queryset(self, request, queryset):
        now = timezone.now()

        if self.value() == '1h':
            threshold = now - timedelta(hours=1)
            return queryset.filter(created_at__gte=threshold)
        elif self.value() == '24h':
            threshold = now - timedelta(hours=24)
            return queryset.filter(created_at__gte=threshold)
        elif self.value() == '7d':
            threshold = now - timedelta(days=7)
            return queryset.filter(created_at__gte=threshold)
        elif self.value() == '30d':
            threshold = now - timedelta(days=30)
            return queryset.filter(created_at__gte=threshold)
        elif self.value() == 'today':
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            return queryset.filter(created_at__gte=today_start)
        elif self.value() == 'yesterday':
            yesterday_start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
            yesterday_end = now.replace(hour=0, minute=0, second=0, microsecond=0)
            return queryset.filter(created_at__range=(yesterday_start, yesterday_end))
        return queryset


class BalanceRangeFilter(admin.SimpleListFilter):
    """Filter user balances by amount ranges."""

    title = _('Balance Range (USD)')
    parameter_name = 'balance_range'

    def lookups(self, request, model_admin) -> List[Tuple[str, str]]:
        return [
            ('zero', _('💸 Zero Balance')),
            ('low', _('🪙 Low ($0.01 - $10)')),
            ('medium', _('💰 Medium ($10 - $100)')),
            ('high', _('💎 High ($100 - $1,000)')),
            ('whale', _('🐋 Whale ($1,000+)')),
            ('negative', _('⚠️ Negative Balance')),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'zero':
            return queryset.filter(balance_usd=0)
        elif self.value() == 'low':
            return queryset.filter(balance_usd__gt=0, balance_usd__lte=10)
        elif self.value() == 'medium':
            return queryset.filter(balance_usd__gt=10, balance_usd__lte=100)
        elif self.value() == 'high':
            return queryset.filter(balance_usd__gt=100, balance_usd__lte=1000)
        elif self.value() == 'whale':
            return queryset.filter(balance_usd__gt=1000)
        elif self.value() == 'negative':
            return queryset.filter(balance_usd__lt=0)
        return queryset


class TransactionTypeFilter(admin.SimpleListFilter):
    """Filter transactions by type."""

    title = _('Transaction Type')
    parameter_name = 'transaction_type_filter'

    def lookups(self, request, model_admin) -> List[Tuple[str, str]]:
        return [
            ('deposit', _('💰 Deposits')),
            ('withdrawal', _('💸 Withdrawals')),
            ('credits', _('➕ Credits (Positive)')),
            ('debits', _('➖ Debits (Negative)')),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'deposit':
            return queryset.filter(transaction_type='deposit')
        elif self.value() == 'withdrawal':
            return queryset.filter(transaction_type='withdrawal')
        elif self.value() == 'credits':
            return queryset.filter(amount_usd__gt=0)
        elif self.value() == 'debits':
            return queryset.filter(amount_usd__lt=0)
        return queryset


class WithdrawalStatusFilter(admin.SimpleListFilter):
    """Filter withdrawal requests by status."""

    title = _('Withdrawal Status')
    parameter_name = 'withdrawal_status'

    def lookups(self, request, model_admin) -> List[Tuple[str, str]]:
        return [
            ('pending', _('⏳ Pending')),
            ('approved', _('✅ Approved')),
            ('processing', _('🔄 Processing')),
            ('completed', _('✅ Completed')),
            ('rejected', _('❌ Rejected')),
            ('cancelled', _('🚫 Cancelled')),
            ('needs_review', _('👁️ Needs Review (Pending/Approved)')),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'needs_review':
            return queryset.filter(status__in=['pending', 'approved'])
        elif self.value():
            return queryset.filter(status=self.value())
        return queryset
