"""
Custom admin filters for payments app.
"""

from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import models
from datetime import timedelta


class PaymentStatusFilter(admin.SimpleListFilter):
    """Filter payments by status."""
    title = _('Payment Status')
    parameter_name = 'payment_status'

    def lookups(self, request, model_admin):
        return (
            ('pending', _('Pending')),
            ('processing', _('Processing')),
            ('completed', _('Completed')),
            ('failed', _('Failed')),
            ('cancelled', _('Cancelled')),
            ('refunded', _('Refunded')),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


class PaymentAmountFilter(admin.SimpleListFilter):
    """Filter payments by amount ranges."""
    title = _('Payment Amount')
    parameter_name = 'payment_amount'

    def lookups(self, request, model_admin):
        return (
            ('small', _('< $10')),
            ('medium', _('$10 - $100')),
            ('large', _('$100 - $1000')),
            ('enterprise', _('> $1000')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'small':
            return queryset.filter(amount_usd__lt=10)
        elif self.value() == 'medium':
            return queryset.filter(amount_usd__gte=10, amount_usd__lt=100)
        elif self.value() == 'large':
            return queryset.filter(amount_usd__gte=100, amount_usd__lt=1000)
        elif self.value() == 'enterprise':
            return queryset.filter(amount_usd__gte=1000)
        return queryset


class SubscriptionStatusFilter(admin.SimpleListFilter):
    """Filter subscriptions by status."""
    title = _('Subscription Status')
    parameter_name = 'subscription_status'

    def lookups(self, request, model_admin):
        return (
            ('active', _('Active')),
            ('inactive', _('Inactive')),
            ('cancelled', _('Cancelled')),
            ('expired', _('Expired')),
            ('trial', _('Trial')),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


class SubscriptionTierFilter(admin.SimpleListFilter):
    """Filter subscriptions by tier."""
    title = _('Subscription Tier')
    parameter_name = 'subscription_tier'

    def lookups(self, request, model_admin):
        return (
            ('basic', _('Basic')),
            ('premium', _('Premium')),
            ('enterprise', _('Enterprise')),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tier=self.value())
        return queryset


class UsageExceededFilter(admin.SimpleListFilter):
    """Filter subscriptions by usage status."""
    title = _('Usage Status')
    parameter_name = 'usage_status'

    def lookups(self, request, model_admin):
        return (
            ('exceeded', _('Usage Exceeded')),
            ('high', _('High Usage (>80%)')),
            ('normal', _('Normal Usage')),
            ('unused', _('No Usage')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'exceeded':
            return queryset.filter(usage_current__gte=models.F('usage_limit'))
        elif self.value() == 'high':
            return queryset.filter(
                usage_current__gte=models.F('usage_limit') * 0.8,
                usage_current__lt=models.F('usage_limit')
            )
        elif self.value() == 'normal':
            return queryset.filter(
                usage_current__gt=0,
                usage_current__lt=models.F('usage_limit') * 0.8
            )
        elif self.value() == 'unused':
            return queryset.filter(usage_current=0)
        return queryset


class APIKeyStatusFilter(admin.SimpleListFilter):
    """Filter API keys by status."""
    title = _('API Key Status')
    parameter_name = 'api_key_status'

    def lookups(self, request, model_admin):
        return (
            ('active', _('Active')),
            ('inactive', _('Inactive')),
            ('expired', _('Expired')),
            ('unused', _('Never Used')),
            ('recent', _('Used Recently')),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == 'active':
            return queryset.filter(is_active=True, expires_at__gt=now)
        elif self.value() == 'inactive':
            return queryset.filter(is_active=False)
        elif self.value() == 'expired':
            return queryset.filter(expires_at__lte=now)
        elif self.value() == 'unused':
            return queryset.filter(last_used__isnull=True)
        elif self.value() == 'recent':
            return queryset.filter(last_used__gte=now - timedelta(days=7))
        return queryset


class CurrencyTypeFilter(admin.SimpleListFilter):
    """Filter currencies by type."""
    title = _('Currency Type')
    parameter_name = 'currency_type'

    def lookups(self, request, model_admin):
        return (
            ('fiat', _('Fiat Currency')),
            ('crypto', _('Cryptocurrency')),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(currency_type=self.value())
        return queryset


class TransactionTypeFilter(admin.SimpleListFilter):
    """Filter transactions by type."""
    title = _('Transaction Type')
    parameter_name = 'transaction_type'

    def lookups(self, request, model_admin):
        return (
            ('credit', _('Credit')),
            ('debit', _('Debit')),
            ('refund', _('Refund')),
            ('withdrawal', _('Withdrawal')),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(transaction_type=self.value())
        return queryset


class RecentActivityFilter(admin.SimpleListFilter):
    """Filter by recent activity."""
    title = _('Recent Activity')
    parameter_name = 'recent_activity'

    def lookups(self, request, model_admin):
        return (
            ('1hour', _('Last Hour')),
            ('24hours', _('Last 24 Hours')),
            ('7days', _('Last 7 Days')),
            ('30days', _('Last 30 Days')),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == '1hour':
            return queryset.filter(created_at__gte=now - timedelta(hours=1))
        elif self.value() == '24hours':
            return queryset.filter(created_at__gte=now - timedelta(hours=24))
        elif self.value() == '7days':
            return queryset.filter(created_at__gte=now - timedelta(days=7))
        elif self.value() == '30days':
            return queryset.filter(created_at__gte=now - timedelta(days=30))
        return queryset


class UserEmailFilter(admin.SimpleListFilter):
    """Filter by user email using text input."""
    title = _('User Email')
    parameter_name = 'user_email'

    def lookups(self, request, model_admin):
        """Return empty lookups to show text input."""
        return ()

    def queryset(self, request, queryset):
        """Filter queryset based on user email input."""
        if self.value():
            return queryset.filter(user__email__icontains=self.value())
        return queryset


class BalanceRangeFilter(admin.SimpleListFilter):
    """Filter user balances by amount ranges."""
    title = _('Balance Amount')
    parameter_name = 'balance_amount'

    def lookups(self, request, model_admin):
        return (
            ('zero', _('$0')),
            ('low', _('$0.01 - $10')),
            ('medium', _('$10 - $100')),
            ('high', _('$100 - $1000')),
            ('enterprise', _('> $1000')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'zero':
            return queryset.filter(amount_usd=0)
        elif self.value() == 'low':
            return queryset.filter(amount_usd__gt=0, amount_usd__lte=10)
        elif self.value() == 'medium':
            return queryset.filter(amount_usd__gt=10, amount_usd__lte=100)
        elif self.value() == 'high':
            return queryset.filter(amount_usd__gt=100, amount_usd__lte=1000)
        elif self.value() == 'enterprise':
            return queryset.filter(amount_usd__gt=1000)
        return queryset
