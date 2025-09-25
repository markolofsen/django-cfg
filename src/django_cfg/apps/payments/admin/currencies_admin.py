"""
Admin interface for currencies.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.contrib import messages
from django.shortcuts import redirect
from django.core.management import call_command
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin
from unfold.decorators import display, action
from unfold.enums import ActionVariant
from unfold.admin import TabularInline

from ..models import Currency, Network, ProviderCurrency
from .filters import CurrencyTypeFilter


@admin.register(Currency)
class CurrencyAdmin(ModelAdmin):
    """Admin interface for clean base currencies."""
    
    # Custom template to show statistics above listing
    change_list_template = 'admin/payments/currency/change_list.html'
    
    list_display = [
        'code',
        'name', 
        'currency_type',
        'usd_rate_display',
        'provider_count',
        'created_at'
    ]
    
    list_display_links = ['code']
    
    search_fields = ['code', 'name']
    
    list_filter = [
        'currency_type',
        'created_at'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    # Unfold action buttons above listing - only one universal button!
    actions_list = [
        'universal_update_all'
    ]
    
    fieldsets = [
        ('Currency Information', {
            'fields': ['code', 'name', 'currency_type']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    @display(description="USD Rate", ordering='usd_rate')
    def usd_rate_display(self, obj):
        """Show USD exchange rate with cache status."""
        if obj.usd_rate and obj.rate_updated_at:
            # Check if rate is fresh (less than 24 hours)
            from django.utils import timezone
            from datetime import timedelta
            
            is_fresh = timezone.now() - obj.rate_updated_at < timedelta(hours=24)
            color_class = "text-green-600 dark:text-green-400" if is_fresh else "text-orange-600 dark:text-orange-400"
            icon = "🟢" if is_fresh else "🟠"
            
            if obj.currency_type == 'fiat':
                # Fiat currencies show as 1 USD = X CURRENCY  
                tokens_per_usd = 1.0 / float(obj.usd_rate) if obj.usd_rate > 0 else 0
                return format_html(
                    '<span class="{}">{} $1 = {} {}</span><br><small class="text-xs text-gray-500">Updated: {}</small>',
                    color_class,
                    icon,
                    f"{tokens_per_usd:.4f}",
                    obj.code,
                    naturaltime(obj.rate_updated_at)
                )
            else:
                # Crypto currencies show as 1 CURRENCY = X USD
                return format_html(
                    '<span class="{}">{} 1 {} = ${}</span><br><small class="text-xs text-gray-500">Updated: {}</small>',
                    color_class,
                    icon,
                    obj.code,
                    f"{float(obj.usd_rate):.8f}",
                    naturaltime(obj.rate_updated_at)
                )
        else:
            return format_html(
                '<span class="text-gray-500">❌ No rate</span><br><small class="text-xs text-gray-400">Never updated</small>'
            )
    
    @display(description="Providers")
    def provider_count(self, obj):
        """Show how many providers support this currency."""
        count = getattr(obj, 'provider_mappings', obj.provider_currency_set if hasattr(obj, 'provider_currency_set') else []).count()
        if count > 0:
            return format_html(
                '<span class="inline-flex items-center rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-800">{} providers</span>',
                count
            )
        return format_html(
            '<span class="inline-flex items-center rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-800">No providers</span>'
        )
    
    def changelist_view(self, request, extra_context=None):
        """Override changelist view to add default statistics."""
        extra_context = extra_context or {}
        
        try:
            from django.db.models import Count
            
            # Get statistics for template
            total_currencies = Currency.objects.count()
            fiat_count = Currency.objects.filter(currency_type='fiat').count()
            crypto_count = Currency.objects.filter(currency_type='crypto').count()
            
            # Count provider mappings
            total_provider_currencies = ProviderCurrency.objects.count()
            enabled_provider_currencies = ProviderCurrency.objects.filter(is_enabled=True).count()
            
            # Count currencies with USD rates
            currencies_with_rates = Currency.objects.filter(usd_rate__isnull=False).count()
            rate_coverage = (currencies_with_rates / total_currencies * 100) if total_currencies > 0 else 0
            
            # Top popular currencies by provider count
            top_currencies = Currency.objects.annotate(
                provider_count=Count('provider_mappings')
            ).filter(provider_count__gt=0).order_by('-provider_count')[:5]
            
            # Pass data to template
            extra_context.update({
                'total_currencies': total_currencies,
                'fiat_count': fiat_count,
                'crypto_count': crypto_count,
                'total_provider_currencies': total_provider_currencies,
                'enabled_provider_currencies': enabled_provider_currencies,
                'currencies_with_rates': currencies_with_rates,
                'rate_coverage': rate_coverage,
                'top_currencies': top_currencies,
            })
            
        except Exception as e:
            # If stats fail, just log and continue
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to generate currency stats: {e}")
        
        return super().changelist_view(request, extra_context)
    
    
    # Universal Admin Action - ONE BUTTON TO RULE THEM ALL!
    
    @action(
        description="🚀 Universal Update",
        icon="sync",
        variant=ActionVariant.SUCCESS,
        url_path="universal-update"
    )
    def universal_update_all(self, request):
        """Universal update: populate missing currencies + sync providers + update rates + show stats."""
        try:
            import threading
            from django.core.management import call_command
            from django.db.models import Count
            from time import sleep
            
            def background_update():
                """Background task for full update."""
                try:
                    # 1. Populate missing currencies (fast, skip if exists)
                    call_command('manage_currencies', '--populate', '--skip-existing')
                    sleep(1)
                    
                    # 2. Sync all providers (medium)
                    call_command('manage_providers', '--all')
                    sleep(1)
                    
                    # 3. Update USD rates for all currencies (slower)
                    call_command('manage_currencies', '--rates-only')
                    
                except Exception as e:
                    print(f"Background universal update error: {e}")
            
            # Start background update
            thread = threading.Thread(target=background_update)
            thread.daemon = True
            thread.start()
            
            # Show immediate stats while update is running
            total_currencies = Currency.objects.count()
            fiat_count = Currency.objects.filter(currency_type='fiat').count()
            crypto_count = Currency.objects.filter(currency_type='crypto').count()
            total_provider_currencies = ProviderCurrency.objects.count()
            enabled_provider_currencies = ProviderCurrency.objects.filter(is_enabled=True).count()
            
            # Top popular currencies by provider count
            top_currencies = Currency.objects.annotate(
                provider_count=Count('provider_mappings')
            ).filter(provider_count__gt=0).order_by('-provider_count')[:5]
            
            currency_list = ""
            for currency in top_currencies:
                currency_list += f'<li class="text-font-default-light dark:text-font-default-dark"><span class="font-semibold text-primary-600 dark:text-primary-500">{currency.code}:</span> {currency.provider_count} providers</li>'
            
            stats_and_status_html = f'''
            <div class="bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 p-5 rounded-default border-l-4 border-green-500 mt-3">
                <h3 class="text-lg font-semibold text-font-important-light dark:text-font-important-dark mb-4">🚀 Universal Update Started</h3>
                
                <div class="bg-yellow-50 dark:bg-yellow-900/20 p-3 rounded-default mb-4 border border-yellow-200 dark:border-yellow-700">
                    <p class="text-yellow-800 dark:text-yellow-200 font-medium">⏳ Background tasks running:</p>
                    <ul class="text-sm text-yellow-700 dark:text-yellow-300 mt-2 space-y-1">
                        <li>1️⃣ Populating missing currencies...</li>
                        <li>2️⃣ Syncing provider data...</li>
                        <li>3️⃣ Updating USD exchange rates...</li>
                    </ul>
                    <p class="text-xs text-yellow-600 dark:text-yellow-400 mt-2">💡 Refresh page in 2-3 minutes to see results</p>
                </div>
                
                <h4 class="font-semibold text-font-important-light dark:text-font-important-dark mb-3">📊 Current Statistics</h4>
                
                <div class="grid grid-cols-2 gap-4 mb-4">
                    <div class="bg-white border border-base-200 dark:bg-base-900 dark:border-base-700 p-3 rounded-default">
                        <span class="text-sm text-font-subtle-light dark:text-font-subtle-dark">Total currencies</span>
                        <p class="text-xl font-bold text-font-important-light dark:text-font-important-dark">{total_currencies}</p>
                    </div>
                    <div class="bg-white border border-base-200 dark:bg-base-900 dark:border-base-700 p-3 rounded-default">
                        <span class="text-sm text-font-subtle-light dark:text-font-subtle-dark">Provider Mappings</span>
                        <p class="text-xl font-bold">
                            <span class="text-green-600 dark:text-green-400">{enabled_provider_currencies}</span>
                            <span class="text-font-subtle-light dark:text-font-subtle-dark mx-1">/</span>
                            <span class="text-gray-600 dark:text-gray-400">{total_provider_currencies}</span>
                        </p>
                    </div>
                </div>
                
                <div class="grid grid-cols-2 gap-4 mb-4">
                    <div class="bg-white border border-base-200 dark:bg-base-900 dark:border-base-700 p-3 rounded-default">
                        <span class="text-sm text-font-subtle-light dark:text-font-subtle-dark">Fiat currencies</span>
                        <p class="text-xl font-bold text-blue-600 dark:text-blue-400">{fiat_count}</p>
                    </div>
                    <div class="bg-white border border-base-200 dark:bg-base-900 dark:border-base-700 p-3 rounded-default">
                        <span class="text-sm text-font-subtle-light dark:text-font-subtle-dark">Cryptocurrencies</span>
                        <p class="text-xl font-bold text-orange-600 dark:text-orange-400">{crypto_count}</p>
                    </div>
                </div>
                
                <div class="bg-white border border-base-200 dark:bg-base-900 dark:border-base-700 p-3 rounded-default">
                    <h4 class="font-semibold text-font-important-light dark:text-font-important-dark mb-2">🚀 Most Supported Currencies</h4>
                    <ul class="space-y-1 text-sm">
                        {currency_list}
                    </ul>
                </div>
            </div>
            '''
            
            messages.success(request, mark_safe(stats_and_status_html))
            
        except Exception as e:
            messages.error(
                request, 
                f"❌ Failed to start universal update: {str(e)}"
            )
        
        return redirect(request.META.get('HTTP_REFERER', '/admin/django_cfg_payments/currency/'))



# ===== NEW ADMIN CLASSES FOR NEW ARCHITECTURE =====



@admin.register(Network)
class NetworkAdmin(ModelAdmin):
    """Admin for blockchain networks."""
    
    list_display = ["code", "name", "currency_count", "created_at"]
    search_fields = ["code", "name"]
    
    @display(description="Currencies")
    def currency_count(self, obj):
        """Show currency count."""
        count = ProviderCurrency.objects.filter(network=obj).count()
        return f"{count} currencies"


@admin.register(ProviderCurrency)
class ProviderCurrencyAdmin(ModelAdmin):
    """Admin for provider currencies."""
    
    list_display = [
        "provider_currency_code",
        "provider_name", 
        "base_currency",
        "network",
        "usd_value_display",
        "status_badges"
    ]
    
    list_filter = [
        "provider_name",
        "is_enabled", 
        "is_popular",
        "is_stable"
    ]
    
    search_fields = [
        "provider_currency_code",
        "base_currency__code"
    ]
    
    @display(description="USD Value")
    def usd_value_display(self, obj):
        """Show USD value for this provider currency."""
        try:
            usd_rate = obj.usd_rate
            tokens_per_usd = obj.tokens_per_usd
            
            if obj.base_currency.currency_type == 'fiat':
                # Fiat: show how many tokens for $1
                return format_html(
                    '<span class="text-blue-600 dark:text-blue-400">$1 = {} {}</span>',
                    f"{tokens_per_usd:.4f}",
                    obj.base_currency.code
                )
            else:
                # Crypto: show USD value
                if usd_rate > 1:
                    # High value crypto (like BTC)
                    return format_html(
                        '<span class="text-green-600 dark:text-green-400 font-semibold">1 {} = ${}</span>',
                        obj.base_currency.code,
                        f"{usd_rate:,.2f}"
                    )
                elif usd_rate > 0.01:
                    # Medium value crypto
                    return format_html(
                        '<span class="text-green-600 dark:text-green-400">1 {} = ${}</span>',
                        obj.base_currency.code,
                        f"{usd_rate:.4f}"
                    )
                else:
                    # Low value crypto (show more decimals)
                    return format_html(
                        '<span class="text-green-600 dark:text-green-400">1 {} = ${}</span>',
                        obj.base_currency.code,
                        f"{usd_rate:.8f}"
                    )
        except Exception as e:
            return format_html(
                '<span class="text-red-500">Error: {}</span>',
                str(e)[:20]
            )
    
    @display(description="Status")
    def status_badges(self, obj):
        """Display status badges."""
        badges = []
        if obj.is_enabled:
            badges.append("✅ Enabled")
        if obj.is_popular:
            badges.append("⭐ Popular") 
        if obj.is_stable:
            badges.append("🔒 Stable")
        return " | ".join(badges) if badges else "❌ Disabled"

