"""
Currency Admin interfaces with Unfold integration.

Includes universal currency/rate update functionality and modern UI.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.contrib import messages
from django.shortcuts import redirect
from django.core.management import call_command
from django.utils.safestring import mark_safe
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import threading
from typing import Optional

from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display, action
from unfold.enums import ActionVariant

from ..models import Currency, Network, ProviderCurrency
from .filters import CurrencyTypeFilter, CurrencyRateStatusFilter
from django_cfg.modules.django_logger import get_logger

logger = get_logger("currencies_admin")


@admin.register(Currency)
class CurrencyAdmin(ModelAdmin):
    """
    Modern Currency admin with Unfold styling and universal update functionality.
    
    Features:
    - Real-time USD rate display with freshness indicators
    - Universal update button (populate + sync + rates)
    - Advanced filtering and search
    - Provider count statistics
    - Integration with django_currency module
    """
    
    # Custom template for statistics dashboard
    change_list_template = 'admin/payments/currency/change_list.html'
    
    list_display = [
        'code_display',
        'name_display', 
        'currency_type_badge',
        'usd_rate_display',
        'provider_count_badge',
        'rate_freshness',
        'created_at_display'
    ]
    
    list_display_links = ['code_display']
    
    search_fields = [
        'code', 
        'name',
        'symbol'
    ]
    
    list_filter = [
        CurrencyTypeFilter,
        CurrencyRateStatusFilter,
        'is_active',
        'created_at'
    ]
    
    readonly_fields = [
        'created_at', 
        'updated_at',
        'exchange_rate_source'
    ]
    
    # Unfold actions
    actions_list = [
        'universal_update_all',
        'update_selected_rates',
        'sync_provider_currencies'
    ]
    
    fieldsets = [
        ('Currency Information', {
            'fields': [
                'code', 
                'name', 
                'currency_type',
                'symbol',
                'decimal_places'
            ]
        }),
        ('Status & Configuration', {
            'fields': [
                'is_active',
                'exchange_rate_source'
            ]
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    def get_queryset(self, request):
        """Optimize queryset with provider count annotation."""
        return super().get_queryset(request).annotate(
            provider_count=Count('provider_configs')
        ).select_related()
    
    @display(description="Code", ordering='code')
    def code_display(self, obj):
        """Display currency code with symbol."""
        if obj.symbol:
            return format_html(
                '<span class="font-mono font-bold text-primary-600 dark:text-primary-400">{}</span> '
                '<span class="text-gray-500 text-sm">{}</span>',
                obj.code,
                obj.symbol
            )
        return format_html(
            '<span class="font-mono font-bold text-primary-600 dark:text-primary-400">{}</span>',
            obj.code
        )
    
    @display(description="Name", ordering='name')
    def name_display(self, obj):
        """Display currency name with truncation."""
        if len(obj.name) > 25:
            return format_html(
                '<span title="{}">{}</span>',
                obj.name,
                obj.name[:22] + "..."
            )
        return obj.name
    
    @display(description="Type", ordering='currency_type')
    def currency_type_badge(self, obj):
        """Display currency type with colored badge."""
        if obj.currency_type == Currency.CurrencyType.FIAT:
            return format_html(
                '<span class="inline-flex items-center rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-800 dark:bg-blue-900 dark:text-blue-200">'
                '💰 Fiat'
                '</span>'
            )
        else:
            return format_html(
                '<span class="inline-flex items-center rounded-full bg-orange-100 px-2.5 py-0.5 text-xs font-medium text-orange-800 dark:bg-orange-900 dark:text-orange-200">'
                '₿ Crypto'
                '</span>'
            )
    
    @display(description="USD Rate", ordering='provider_configs__usd_rate')
    def usd_rate_display(self, obj):
        """Display USD rate with freshness indicator."""
        # Get the most recent rate from ProviderCurrency
        provider_currency = obj.provider_configs_set.filter(
            usd_rate__isnull=False
        ).order_by('-updated_at').first()
        
        if not provider_currency or not provider_currency.usd_rate:
            return format_html(
                '<span class="text-red-500 text-sm">❌ No rate</span>'
            )
        
        # Check freshness (24 hours)
        is_fresh = (
            provider_currency.updated_at and 
            timezone.now() - provider_currency.updated_at < timedelta(hours=24)
        )
        
        color_class = "text-green-600 dark:text-green-400" if is_fresh else "text-orange-600 dark:text-orange-400"
        icon = "🟢" if is_fresh else "🟠"
        
        if obj.currency_type == Currency.CurrencyType.FIAT:
            # Fiat: show 1 USD = X CURRENCY
            tokens_per_usd = 1.0 / float(provider_currency.usd_rate) if provider_currency.usd_rate > 0 else 0
            return format_html(
                '<div class="{}">{} $1 = {} {}</div>'
                '<small class="text-xs text-gray-500">Updated: {}</small>',
                color_class,
                icon,
                f"{tokens_per_usd:.4f}",
                obj.code,
                naturaltime(provider_currency.updated_at) if provider_currency.updated_at else "Never"
            )
        else:
            # Crypto: show 1 CURRENCY = X USD
            usd_rate = float(provider_currency.usd_rate)
            if usd_rate > 1:
                rate_display = f"${usd_rate:,.2f}"
            elif usd_rate > 0.01:
                rate_display = f"${usd_rate:.4f}"
            else:
                rate_display = f"${usd_rate:.8f}"
                
            return format_html(
                '<div class="{}">{} 1 {} = {}</div>'
                '<small class="text-xs text-gray-500">Updated: {}</small>',
                color_class,
                icon,
                obj.code,
                rate_display,
                naturaltime(provider_currency.updated_at) if provider_currency.updated_at else "Never"
            )
    
    @display(description="Providers")
    def provider_count_badge(self, obj):
        """Display provider count with badge."""
        count = getattr(obj, 'provider_count', 0)
        if count > 0:
            return format_html(
                '<span class="inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800 dark:bg-green-900 dark:text-green-200">'
                '{} provider{}'
                '</span>',
                count,
                's' if count != 1 else ''
            )
        return format_html(
            '<span class="inline-flex items-center rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-800 dark:bg-gray-900 dark:text-gray-200">'
            'No providers'
            '</span>'
        )
    
    @display(description="Rate Status")
    def rate_freshness(self, obj):
        """Display rate freshness indicator."""
        provider_currency = obj.provider_configs_set.filter(
            usd_rate__isnull=False
        ).order_by('-updated_at').first()
        
        if not provider_currency or not provider_currency.updated_at:
            return format_html('<span class="text-red-500">❌ Never</span>')
        
        age = timezone.now() - provider_currency.updated_at
        
        if age < timedelta(hours=1):
            return format_html('<span class="text-green-500">🟢 Fresh</span>')
        elif age < timedelta(hours=24):
            return format_html('<span class="text-yellow-500">🟡 Recent</span>')
        elif age < timedelta(days=7):
            return format_html('<span class="text-orange-500">🟠 Stale</span>')
        else:
            return format_html('<span class="text-red-500">🔴 Old</span>')
    
    @display(description="Created", ordering='created_at')
    def created_at_display(self, obj):
        """Display creation date."""
        return naturaltime(obj.created_at)
    
    def changelist_view(self, request, extra_context=None):
        """Add statistics to changelist context."""
        extra_context = extra_context or {}
        
        try:
            # Basic statistics
            total_currencies = Currency.objects.count()
            fiat_count = Currency.objects.filter(currency_type=Currency.CurrencyType.FIAT).count()
            crypto_count = Currency.objects.filter(currency_type=Currency.CurrencyType.CRYPTO).count()
            active_count = Currency.objects.filter(is_active=True).count()
            
            # Provider statistics
            total_provider_currencies = ProviderCurrency.objects.count()
            enabled_provider_currencies = ProviderCurrency.objects.filter(is_enabled=True).count()
            
            # Rate statistics
            currencies_with_rates = Currency.objects.filter(
                provider_configs__usd_rate__isnull=False
            ).distinct().count()
            rate_coverage = (currencies_with_rates / total_currencies * 100) if total_currencies > 0 else 0
            
            # Fresh rates (updated in last 24 hours)
            fresh_threshold = timezone.now() - timedelta(hours=24)
            fresh_rates_count = Currency.objects.filter(
                provider_configs__updated_at__gte=fresh_threshold
            ).distinct().count()
            
            # Top currencies by provider count
            top_currencies = Currency.objects.annotate(
                provider_count=Count('provider_configs')
            ).filter(provider_count__gt=0).order_by('-provider_count')[:5]
            
            extra_context.update({
                'currency_stats': {
                    'total_currencies': total_currencies,
                    'fiat_count': fiat_count,
                    'crypto_count': crypto_count,
                    'active_count': active_count,
                    'total_provider_currencies': total_provider_currencies,
                    'enabled_provider_currencies': enabled_provider_currencies,
                    'currencies_with_rates': currencies_with_rates,
                    'rate_coverage': rate_coverage,
                    'fresh_rates_count': fresh_rates_count,
                    'top_currencies': top_currencies,
                }
            })
            
        except Exception as e:
            logger.warning(f"Failed to generate currency statistics: {e}")
            extra_context['currency_stats'] = None
        
        return super().changelist_view(request, extra_context)
    
    # ===== ADMIN ACTIONS =====
    
    @action(
        description="🚀 Universal Update (All)",
        icon="sync",
        variant=ActionVariant.SUCCESS,
        url_path="universal-update"
    )
    def universal_update_all(self, request):
        """
        Universal update: populate currencies + sync providers + update rates.
        
        This is the main action that performs a complete system update.
        """
        try:
            def background_update():
                """Background task for comprehensive update."""
                try:
                    logger.info("Starting universal currency update")
                    
                    # 1. Populate missing currencies (fast)
                    call_command('manage_currencies', '--populate', '--skip-existing')
                    
                    # 2. Sync all providers (medium speed)
                    call_command('manage_providers', '--all')
                    
                    # 3. Update USD rates (slower)
                    call_command('manage_currencies', '--rates-only')
                    
                    logger.info("Universal currency update completed successfully")
                    
                except Exception as e:
                    logger.error(f"Universal update failed: {e}")
            
            # Start background update
            thread = threading.Thread(target=background_update)
            thread.daemon = True
            thread.start()
            
            # Generate immediate statistics for user feedback
            stats = self._get_current_stats()
            
            success_message = self._generate_update_message(stats)
            messages.success(request, mark_safe(success_message))
            
            logger.info(f"Universal update initiated by user {request.user.username}")
            
        except Exception as e:
            error_msg = f"❌ Failed to start universal update: {str(e)}"
            messages.error(request, error_msg)
            logger.error(f"Universal update initiation failed: {e}")
        
        return redirect(request.META.get('HTTP_REFERER', '/admin/payments/currency/'))
    
    @action(
        description="💱 Update Selected Rates",
        icon="trending_up",
        variant=ActionVariant.WARNING
    )
    def update_selected_rates(self, request, queryset):
        """Update USD rates for selected currencies only."""
        try:
            currency_codes = list(queryset.values_list('code', flat=True))
            
            def background_rate_update():
                """Background task for rate updates."""
                try:
                    for code in currency_codes:
                        call_command('manage_currencies', '--currency', code, '--rates-only')
                except Exception as e:
                    logger.error(f"Selected rate update failed: {e}")
            
            thread = threading.Thread(target=background_rate_update)
            thread.daemon = True
            thread.start()
            
            messages.success(
                request,
                f"💱 Started rate update for {len(currency_codes)} currencies: {', '.join(currency_codes[:5])}"
                f"{'...' if len(currency_codes) > 5 else ''}"
            )
            
        except Exception as e:
            messages.error(request, f"❌ Failed to update rates: {str(e)}")
    
    @action(
        description="🔄 Sync Provider Currencies",
        icon="cloud_sync",
        variant=ActionVariant.INFO
    )
    def sync_provider_currencies(self, request, queryset):
        """Sync provider currencies for selected base currencies."""
        try:
            currency_codes = list(queryset.values_list('code', flat=True))
            
            def background_sync():
                """Background task for provider sync."""
                try:
                    call_command('manage_providers', '--all', '--currencies', ','.join(currency_codes))
                except Exception as e:
                    logger.error(f"Provider sync failed: {e}")
            
            thread = threading.Thread(target=background_sync)
            thread.daemon = True
            thread.start()
            
            messages.success(
                request,
                f"🔄 Started provider sync for {len(currency_codes)} currencies"
            )
            
        except Exception as e:
            messages.error(request, f"❌ Failed to sync providers: {str(e)}")
    
    # ===== HELPER METHODS =====
    
    def _get_current_stats(self) -> dict:
        """Get current system statistics."""
        try:
            return {
                'total_currencies': Currency.objects.count(),
                'fiat_count': Currency.objects.filter(currency_type=Currency.CurrencyType.FIAT).count(),
                'crypto_count': Currency.objects.filter(currency_type=Currency.CurrencyType.CRYPTO).count(),
                'total_provider_currencies': ProviderCurrency.objects.count(),
                'enabled_provider_currencies': ProviderCurrency.objects.filter(is_enabled=True).count(),
                'top_currencies': Currency.objects.annotate(
                    provider_count=Count('provider_configs')
                ).filter(provider_count__gt=0).order_by('-provider_count')[:3]
            }
        except Exception as e:
            logger.warning(f"Failed to get current stats: {e}")
            return {}
    
    def _generate_update_message(self, stats: dict) -> str:
        """Generate HTML message for update status."""
        top_currencies_html = ""
        if 'top_currencies' in stats:
            for currency in stats['top_currencies']:
                provider_count = getattr(currency, 'provider_count', 0)
                top_currencies_html += f'<li><strong>{currency.code}:</strong> {provider_count} providers</li>'
        
        return f'''
        <div class="bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 p-4 rounded-lg border-l-4 border-green-500">
            <h3 class="text-lg font-semibold text-green-800 dark:text-green-200 mb-3">🚀 Universal Update Started</h3>
            
            <div class="bg-yellow-50 dark:bg-yellow-900/20 p-3 rounded-lg mb-3 border border-yellow-200 dark:border-yellow-700">
                <p class="text-yellow-800 dark:text-yellow-200 font-medium">⏳ Background tasks running:</p>
                <ul class="text-sm text-yellow-700 dark:text-yellow-300 mt-2 space-y-1">
                    <li>1️⃣ Populating missing currencies...</li>
                    <li>2️⃣ Syncing provider data...</li>
                    <li>3️⃣ Updating USD exchange rates...</li>
                </ul>
                <p class="text-xs text-yellow-600 dark:text-yellow-400 mt-2">💡 Refresh page in 2-3 minutes to see results</p>
            </div>
            
            <div class="grid grid-cols-3 gap-3 mb-3">
                <div class="bg-white dark:bg-gray-800 p-3 rounded-lg border">
                    <span class="text-sm text-gray-600 dark:text-gray-400">Total Currencies</span>
                    <p class="text-xl font-bold text-gray-900 dark:text-gray-100">{stats.get('total_currencies', 0)}</p>
                </div>
                <div class="bg-white dark:bg-gray-800 p-3 rounded-lg border">
                    <span class="text-sm text-gray-600 dark:text-gray-400">Fiat / Crypto</span>
                    <p class="text-xl font-bold">
                        <span class="text-blue-600">{stats.get('fiat_count', 0)}</span> / 
                        <span class="text-orange-600">{stats.get('crypto_count', 0)}</span>
                    </p>
                </div>
                <div class="bg-white dark:bg-gray-800 p-3 rounded-lg border">
                    <span class="text-sm text-gray-600 dark:text-gray-400">Provider Mappings</span>
                    <p class="text-xl font-bold text-green-600">{stats.get('enabled_provider_currencies', 0)}</p>
                </div>
            </div>
            
            {f'<div class="bg-white dark:bg-gray-800 p-3 rounded-lg border"><h4 class="font-semibold mb-2">🚀 Top Currencies</h4><ul class="text-sm space-y-1">{top_currencies_html}</ul></div>' if top_currencies_html else ''}
        </div>
        '''


@admin.register(Network)
class NetworkAdmin(ModelAdmin):
    """Admin interface for blockchain networks."""
    
    list_display = [
        'code_display',
        'name_display',
        'currency_count_badge',
        'created_at_display'
    ]
    
    search_fields = ['code', 'name']
    
    readonly_fields = ['created_at', 'updated_at']
    
    @display(description="Code", ordering='code')
    def code_display(self, obj):
        """Display network code with styling."""
        return format_html(
            '<span class="font-mono font-bold text-purple-600 dark:text-purple-400">{}</span>',
            obj.code
        )
    
    @display(description="Name", ordering='name')
    def name_display(self, obj):
        """Display network name."""
        return obj.name
    
    @display(description="Currencies")
    def currency_count_badge(self, obj):
        """Display currency count for this network."""
        count = ProviderCurrency.objects.filter(network=obj).count()
        if count > 0:
            return format_html(
                '<span class="inline-flex items-center rounded-full bg-purple-100 px-2.5 py-0.5 text-xs font-medium text-purple-800 dark:bg-purple-900 dark:text-purple-200">'
                '{} currenc{}'
                '</span>',
                count,
                'ies' if count != 1 else 'y'
            )
        return format_html(
            '<span class="inline-flex items-center rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-800 dark:bg-gray-900 dark:text-gray-200">'
            'No currencies'
            '</span>'
        )
    
    @display(description="Created", ordering='created_at')
    def created_at_display(self, obj):
        """Display creation date."""
        return naturaltime(obj.created_at)


@admin.register(ProviderCurrency)
class ProviderCurrencyAdmin(ModelAdmin):
    """Admin interface for provider-specific currency configurations."""
    
    list_display = [
        'provider_currency_code_display',
        'provider_name_badge',
        'base_currency_display',
        'network_display',
        'usd_value_display',
        'status_badges',
        'updated_at_display'
    ]
    
    list_filter = [
        'provider',
        'is_enabled',
        'currency__currency_type',
        'network'
    ]
    
    search_fields = [
        'provider_currency_code',
        'currency__code',
        'currency__name',
        'network__code'
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at'
    ]
    
    def get_queryset(self, request):
        """Optimize queryset with related objects."""
        return super().get_queryset(request).select_related(
            'currency', 'network'
        )
    
    @display(description="Provider Code", ordering='provider_currency_code')
    def provider_currency_code_display(self, obj):
        """Display provider-specific currency code."""
        return format_html(
            '<span class="font-mono text-sm bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">{}</span>',
            obj.provider_currency_code
        )
    
    @display(description="Provider", ordering='provider')
    def provider_name_badge(self, obj):
        """Display provider name with badge."""
        color_map = {
            'nowpayments': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
            'cryptomus': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
            'cryptapi': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
        }
        
        color_class = color_map.get(obj.provider.lower(), 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200')
        
        return format_html(
            '<span class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium {}">{}</span>',
            color_class,
            obj.provider.title()
        )
    
    @display(description="Currency", ordering='currency__code')
    def base_currency_display(self, obj):
        """Display base currency with type indicator."""
        type_icon = "💰" if obj.currency.currency_type == Currency.CurrencyType.FIAT else "₿"
        return format_html(
            '{} <span class="font-bold">{}</span>',
            type_icon,
            obj.currency.code
        )
    
    @display(description="Network", ordering='network__code')
    def network_display(self, obj):
        """Display network information."""
        if obj.network:
            return format_html(
                '<span class="text-purple-600 dark:text-purple-400">{}</span>',
                obj.network.code
            )
        return format_html('<span class="text-gray-500">—</span>')
    
    @display(description="USD Value")
    def usd_value_display(self, obj):
        """Display USD value with proper formatting."""
        try:
            if not obj.usd_rate:
                return format_html('<span class="text-gray-500">No rate</span>')
            
            usd_rate = float(obj.usd_rate)
            
            if obj.currency.currency_type == Currency.CurrencyType.FIAT:
                # Fiat: show tokens per USD
                tokens_per_usd = 1.0 / usd_rate if usd_rate > 0 else 0
                return format_html(
                    '<span class="text-blue-600 dark:text-blue-400">$1 = {} {}</span>',
                    f"{tokens_per_usd:.4f}",
                    obj.currency.code
                )
            else:
                # Crypto: show USD value
                if usd_rate > 1000:
                    rate_display = f"${usd_rate:,.0f}"
                elif usd_rate > 1:
                    rate_display = f"${usd_rate:,.2f}"
                elif usd_rate > 0.01:
                    rate_display = f"${usd_rate:.4f}"
                else:
                    rate_display = f"${usd_rate:.8f}"
                
                return format_html(
                    '<span class="text-green-600 dark:text-green-400">1 {} = {}</span>',
                    obj.currency.code,
                    rate_display
                )
                
        except Exception as e:
            return format_html(
                '<span class="text-red-500">Error: {}</span>',
                str(e)[:15]
            )
    
    @display(description="Status")
    def status_badges(self, obj):
        """Display status badges."""
        badges = []
        
        if obj.is_enabled:
            badges.append('<span class="inline-flex items-center rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-800 dark:bg-green-900 dark:text-green-200">✅ Enabled</span>')
        else:
            badges.append('<span class="inline-flex items-center rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-800 dark:bg-red-900 dark:text-red-200">❌ Disabled</span>')
        
        # Note: is_popular and is_stable fields don't exist in model
        # These could be added later or calculated based on other criteria
        
        return format_html(' '.join(badges))
    
    @display(description="Updated", ordering='updated_at')
    def updated_at_display(self, obj):
        """Display last update time."""
        return naturaltime(obj.updated_at)
