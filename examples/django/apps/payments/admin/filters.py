"""
Custom admin filters for the Universal Payment System v2.0.

Provides advanced filtering capabilities for the Unfold admin interface.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Q, Count
from django.contrib.auth import get_user_model

from datetime import timedelta
from typing import List, Tuple, Optional

from ..models import Currency, UniversalPayment, UserBalance, Subscription, APIKey, ProviderCurrency


class CurrencyTypeFilter(admin.SimpleListFilter):
    """Filter currencies by type with enhanced options."""
    
    title = _('Currency Type')
    parameter_name = 'currency_type'
    
    def lookups(self, request, model_admin) -> List[Tuple[str, str]]:
        return [
            ('fiat', _('💰 Fiat Currencies')),
            ('crypto', _('₿ Cryptocurrencies')),
            ('active_fiat', _('💰 Active Fiat')),
            ('active_crypto', _('₿ Active Crypto')),
        ]
    
    def queryset(self, request, queryset):
        if self.value() == 'fiat':
            return queryset.filter(currency_type=Currency.CurrencyType.FIAT)
        elif self.value() == 'crypto':
            return queryset.filter(currency_type=Currency.CurrencyType.CRYPTO)
        elif self.value() == 'active_fiat':
            return queryset.filter(
                currency_type=Currency.CurrencyType.FIAT,
                is_active=True
            )
        elif self.value() == 'active_crypto':
            return queryset.filter(
                currency_type=Currency.CurrencyType.CRYPTO,
                is_active=True
            )
        return queryset


class CurrencyRateStatusFilter(admin.SimpleListFilter):
    """Filter currencies by USD rate status."""
    
    title = _('Rate Status')
    parameter_name = 'rate_status'
    
    def lookups(self, request, model_admin) -> List[Tuple[str, str]]:
        return [
            ('has_rate', _('🟢 Has USD Rate')),
            ('no_rate', _('❌ No USD Rate')),
            ('fresh_rate', _('🟢 Fresh Rate (24h)')),
            ('stale_rate', _('🟠 Stale Rate (>24h)')),
            ('old_rate', _('🔴 Old Rate (>7d)')),
        ]
    
    def queryset(self, request, queryset):
        now = timezone.now()
        
        if self.value() == 'has_rate':
            return queryset.filter(provider_configs__usd_rate__isnull=False).distinct()
        elif self.value() == 'no_rate':
            return queryset.exclude(provider_configs__usd_rate__isnull=False).distinct()
        elif self.value() == 'fresh_rate':
            fresh_threshold = now - timedelta(hours=24)
            return queryset.filter(
                provider_configs__rate_updated_at__gte=fresh_threshold
            ).distinct()
        elif self.value() == 'stale_rate':
            stale_start = now - timedelta(days=7)
            stale_end = now - timedelta(hours=24)
            return queryset.filter(
                provider_configs__rate_updated_at__range=(stale_start, stale_end)
            ).distinct()
        elif self.value() == 'old_rate':
            old_threshold = now - timedelta(days=7)
            return queryset.filter(
                provider_configs__rate_updated_at__lt=old_threshold
            ).distinct()
        return queryset


class CurrencyProviderFilter(admin.SimpleListFilter):
    """Filter currencies by payment provider support."""
    
    title = _('Provider Support')
    parameter_name = 'provider_support'
    
    def lookups(self, request, model_admin) -> List[Tuple[str, str]]:
        """Get available providers from database."""
        try:
            # Get unique providers from ProviderCurrency
            providers = ProviderCurrency.objects.values_list('provider', flat=True).distinct().order_by('provider')
            
            lookups = []
            
            # Add provider-specific filters
            for provider in providers:
                if provider:
                    provider_display = provider.replace('_', ' ').title()
                    # Get count of currencies for this provider
                    count = Currency.objects.filter(
                        provider_configs__provider=provider,
                        provider_configs__is_enabled=True
                    ).distinct().count()
                    
                    if count > 0:
                        lookups.append((
                            provider,
                            f'🔗 {provider_display} ({count})'
                        ))
            
            # Add special filters
            lookups.extend([
                ('any_provider', _('🌐 Any Provider')),
                ('no_provider', _('❌ No Provider')),
                ('multiple_providers', _('🔄 Multiple Providers')),
                ('enabled_only', _('✅ Enabled Providers Only')),
            ])
            
            return lookups
            
        except Exception as e:
            # Fallback if database query fails
            return [
                ('nowpayments', _('🔗 NowPayments')),
                ('any_provider', _('🌐 Any Provider')),
                ('no_provider', _('❌ No Provider')),
            ]
    
    def queryset(self, request, queryset):
        """Filter queryset based on provider selection."""
        if not self.value():
            return queryset
            
        if self.value() == 'any_provider':
            # Currencies that have at least one provider
            return queryset.filter(provider_configs__isnull=False).distinct()
            
        elif self.value() == 'no_provider':
            # Currencies that have no provider configurations
            return queryset.filter(provider_configs__isnull=True).distinct()
            
        elif self.value() == 'multiple_providers':
            # Currencies supported by multiple providers
            return queryset.annotate(
                provider_count=Count('provider_configs__provider', distinct=True)
            ).filter(provider_count__gt=1)
            
        elif self.value() == 'enabled_only':
            # Currencies with at least one enabled provider
            return queryset.filter(
                provider_configs__is_enabled=True
            ).distinct()
            
        else:
            # Specific provider filter
            return queryset.filter(
                provider_configs__provider=self.value()
            ).distinct()


class PaymentStatusFilter(admin.SimpleListFilter):
    """Enhanced payment status filter with groupings."""
    
    title = _('Payment Status')
    parameter_name = 'status'
    
    def lookups(self, request, model_admin) -> List[Tuple[str, str]]:
        return [
            ('pending', _('⏳ Pending')),
            ('waiting', _('⏰ Waiting for Payment')),
            ('confirming', _('🔄 Confirming')),
            ('completed', _('✅ Completed')),
            ('failed', _('❌ Failed')),
            ('cancelled', _('🚫 Cancelled')),
            ('expired', _('⌛ Expired')),
            ('refunded', _('↩️ Refunded')),
            ('active', _('🟢 Active (Pending/Waiting/Confirming)')),
            ('finished', _('🏁 Finished (Completed/Failed/Cancelled)')),
        ]
    
    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(
                status__in=[
                    UniversalPayment.PaymentStatus.PENDING,
                    UniversalPayment.PaymentStatus.CONFIRMING
                ]
            )
        elif self.value() == 'finished':
            return queryset.filter(
                status__in=[
                    UniversalPayment.PaymentStatus.COMPLETED,
                    UniversalPayment.PaymentStatus.FAILED,
                    UniversalPayment.PaymentStatus.CANCELLED
                ]
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
            ('micro', _('💵 Micro ($0.01 - $1)')),
            ('small', _('💵 Small ($1 - $10)')),
            ('medium', _('💰 Medium ($10 - $100)')),
            ('large', _('💰 Large ($100 - $1,000)')),
            ('huge', _('💎 Huge ($1,000+)')),
        ]
    
    def queryset(self, request, queryset):
        if self.value() == 'micro':
            return queryset.filter(amount_usd__gte=0.01, amount_usd__lt=1)
        elif self.value() == 'small':
            return queryset.filter(amount_usd__gte=1, amount_usd__lt=10)
        elif self.value() == 'medium':
            return queryset.filter(amount_usd__gte=10, amount_usd__lt=100)
        elif self.value() == 'large':
            return queryset.filter(amount_usd__gte=100, amount_usd__lt=1000)
        elif self.value() == 'huge':
            return queryset.filter(amount_usd__gte=1000)
        return queryset


class UserEmailFilter(admin.SimpleListFilter):
    """Filter by user email domain."""
    
    title = _('User Email Domain')
    parameter_name = 'email_domain'
    
    def lookups(self, request, model_admin) -> List[Tuple[str, str]]:
        # Get top email domains from the database
        User = get_user_model()
        
        try:
            # This is a simplified approach - in production you might want to cache this
            domains = []
            common_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
            
            for domain in common_domains:
                count = User.objects.filter(email__icontains=f'@{domain}').count()
                if count > 0:
                    domains.append((domain, f'@{domain} ({count})'))
            
            return domains
        except Exception:
            return [
                ('gmail.com', '@gmail.com'),
                ('yahoo.com', '@yahoo.com'),
                ('outlook.com', '@outlook.com'),
            ]
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user__email__icontains=f'@{self.value()}')
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


class SubscriptionTierFilter(admin.SimpleListFilter):
    """Filter subscriptions by tier."""
    
    title = _('Subscription Tier')
    parameter_name = 'tier'
    
    def lookups(self, request, model_admin) -> List[Tuple[str, str]]:
        return [
            ('free', _('🆓 Free Tier')),
            ('basic', _('🥉 Basic Tier')),
            ('premium', _('🥈 Premium Tier')),
            ('enterprise', _('🥇 Enterprise Tier')),
        ]
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tier=self.value())
        return queryset


class SubscriptionStatusFilter(admin.SimpleListFilter):
    """Filter subscriptions by status with enhanced groupings."""
    
    title = _('Subscription Status')
    parameter_name = 'subscription_status'
    
    def lookups(self, request, model_admin) -> List[Tuple[str, str]]:
        return [
            ('active', _('✅ Active')),
            ('expired', _('⌛ Expired')),
            ('cancelled', _('🚫 Cancelled')),
            ('suspended', _('⏸️ Suspended')),
            ('expiring_soon', _('⚠️ Expiring Soon (7 days)')),
            ('recently_expired', _('🔴 Recently Expired (7 days)')),
        ]
    
    def queryset(self, request, queryset):
        now = timezone.now()
        
        if self.value() == 'expiring_soon':
            threshold = now + timedelta(days=7)
            return queryset.filter(
                status=Subscription.SubscriptionStatus.ACTIVE,
                expires_at__lte=threshold,
                expires_at__gt=now
            )
        elif self.value() == 'recently_expired':
            threshold = now - timedelta(days=7)
            return queryset.filter(
                status=Subscription.SubscriptionStatus.EXPIRED,
                expires_at__gte=threshold
            )
        elif self.value():
            return queryset.filter(status=self.value())
        return queryset


class APIKeyStatusFilter(admin.SimpleListFilter):
    """Filter API keys by status and activity."""
    
    title = _('API Key Status')
    parameter_name = 'api_key_status'
    
    def lookups(self, request, model_admin) -> List[Tuple[str, str]]:
        return [
            ('active', _('✅ Active')),
            ('inactive', _('❌ Inactive')),
            ('expired', _('⌛ Expired')),
            ('expiring_soon', _('⚠️ Expiring Soon (7 days)')),
            ('never_used', _('🆕 Never Used')),
            ('recently_used', _('🔥 Recently Used (24h)')),
            ('high_usage', _('📈 High Usage (>1000 requests)')),
        ]
    
    def queryset(self, request, queryset):
        now = timezone.now()
        
        if self.value() == 'active':
            return queryset.filter(is_active=True, expires_at__gt=now)
        elif self.value() == 'inactive':
            return queryset.filter(is_active=False)
        elif self.value() == 'expired':
            return queryset.filter(expires_at__lte=now)
        elif self.value() == 'expiring_soon':
            threshold = now + timedelta(days=7)
            return queryset.filter(
                is_active=True,
                expires_at__lte=threshold,
                expires_at__gt=now
            )
        elif self.value() == 'never_used':
            return queryset.filter(last_used_at__isnull=True)
        elif self.value() == 'recently_used':
            threshold = now - timedelta(hours=24)
            return queryset.filter(last_used_at__gte=threshold)
        elif self.value() == 'high_usage':
            return queryset.filter(total_requests__gte=1000)
        return queryset
