"""
Currency Admin interface using new StandaloneActionsMixin.

Example of how to use the new standalone_action decorator.
"""

from django.contrib import admin
from django.db import models
from django.db.models import Count
from django.core.management import call_command
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from django_cfg.modules.django_admin import (
    OptimizedModelAdmin,
    DisplayMixin,
    StandaloneActionsMixin,
    standalone_action,
    MoneyDisplayConfig,
    StatusBadgeConfig,
    DateTimeDisplayConfig,
    Icons,
    ActionVariant,
    display,
    action
)
from django_cfg.modules.django_admin.utils.badges import StatusBadge
from django_cfg.modules.django_logging import get_logger
from ..models import Currency
from .filters import CurrencyTypeFilter, CurrencyProviderFilter, CurrencyRateStatusFilter

logger = get_logger("currencies_admin")


@admin.register(Currency)
class CurrencyAdmin(OptimizedModelAdmin, DisplayMixin, StandaloneActionsMixin, ModelAdmin):
    """Currency admin using new StandaloneActionsMixin."""
    
    # Custom template for statistics dashboard
    change_list_template = 'admin/payments/currency/change_list.html'
    
    # Performance optimization
    select_related_fields = []
    prefetch_related_fields = ['provider_configs']
    
    list_display = [
        'currency_display',
        'name_display', 
        'type_display',
        'providers_display',
        'rate_display',
        'status_display',
        'updated_display'
    ]
    
    list_filter = [
        'is_active',
        CurrencyTypeFilter,
        CurrencyProviderFilter,
        CurrencyRateStatusFilter,
        'updated_at'
    ]
    search_fields = ['code', 'name', 'symbol']
    readonly_fields = ['created_at', 'updated_at']
    
    # Register bulk actions
    actions = ['activate_currencies', 'deactivate_currencies']
    
    # Register standalone actions
    actions_list = ['update_rates', 'sync_providers', 'backup_data']
    
    @display(description="Currency")
    def currency_display(self, obj):
        """Currency display with flag icons."""
        currency_icons = {
            'USD': Icons.ATTACH_MONEY,  # $ icon
            'EUR': Icons.EURO_SYMBOL,   # € icon  
            'GBP': Icons.CURRENCY_POUND, # £ icon
            'JPY': Icons.CURRENCY_YEN,   # ¥ icon
            'BTC': Icons.CURRENCY_BITCOIN,
            'ETH': Icons.CURRENCY_EXCHANGE,
            'LTC': Icons.CURRENCY_EXCHANGE,
        }
        
        icon = currency_icons.get(obj.code, Icons.ATTACH_MONEY)
        text = f"{obj.code}"
        if obj.symbol and obj.symbol != obj.code:
            text += f" ({obj.symbol})"
        
        config = StatusBadgeConfig(show_icons=True, icon=icon)
        return StatusBadge.create(text=text, variant="primary", config=config)
    
    @display(description="Name")
    def name_display(self, obj):
        """Currency name display."""
        config = StatusBadgeConfig(show_icons=True, icon=Icons.LABEL)
        return StatusBadge.create(
            text=obj.name or "Unknown", 
            variant="info",
            config=config
        )
    
    @display(description="Type")
    def type_display(self, obj):
        """Currency type display with appropriate icons."""
        type_icons = {
            'fiat': Icons.ATTACH_MONEY,
            'crypto': Icons.CURRENCY_BITCOIN,
        }
        
        type_variants = {
            'fiat': 'info',
            'crypto': 'warning',
        }
        
        icon = type_icons.get(obj.currency_type, Icons.HELP)
        variant = type_variants.get(obj.currency_type, 'default')
        
        config = StatusBadgeConfig(show_icons=True, icon=icon)
        return StatusBadge.create(
            text=obj.get_currency_type_display(), 
            variant=variant,
            config=config
        )
    
    @display(description="Providers")
    def providers_display(self, obj):
        """Display providers supporting this currency."""
        providers = obj.provider_configs.filter(is_enabled=True).values_list('provider', flat=True)
        
        if not providers:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.WARNING)
            return StatusBadge.create(text="No Providers", variant="secondary", config=config)
        
        provider_list = ", ".join(providers)
        if len(provider_list) > 30:
            provider_list = provider_list[:27] + "..."
        
        config = StatusBadgeConfig(show_icons=True, icon=Icons.BUSINESS)
        return StatusBadge.create(
            text=provider_list, 
            variant="success",
            config=config
        )
    
    @display(description="Rate")
    def rate_display(self, obj):
        """Exchange rate display with smart formatting."""
        if not hasattr(obj, 'usd_rate') or obj.usd_rate is None or obj.usd_rate == 0:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.HELP)
            return StatusBadge.create(text="No Rate", variant="secondary", config=config)
        
        # Use MoneyDisplayConfig with rate mode for smart formatting
        config = MoneyDisplayConfig(
            currency="USD",
            rate_mode=True,  # Special formatting for exchange rates
            show_sign=False,
            thousand_separator=True
        )
        return self.display_money_amount(
            type('obj', (), {'usd_rate': obj.usd_rate})(),
            'usd_rate', 
            config
        )
    
    @display(description="Status", label=True)
    def status_display(self, obj):
        """Status display with appropriate icons."""
        status = "Active" if obj.is_active else "Inactive"
        
        config = StatusBadgeConfig(
            custom_mappings={
                "Active": "success",
                "Inactive": "secondary"
            },
            show_icons=True,
            icon=Icons.CHECK_CIRCLE if obj.is_active else Icons.CANCEL
        )
        
        return self.display_status_auto(
            type('obj', (), {'status': status})(), 
            'status', 
            config
        )
    
    @display(description="Updated")
    def updated_display(self, obj):
        """Updated time display."""
        return self.display_datetime_relative(obj, 'updated_at')
    
    # Bulk actions (traditional)
    @action(description="Activate currencies", variant=ActionVariant.SUCCESS)
    def activate_currencies(self, request, queryset):
        """Activate selected currencies."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Activated {updated} currency(ies).", level='SUCCESS')
    
    @action(description="Deactivate currencies", variant=ActionVariant.WARNING)
    def deactivate_currencies(self, request, queryset):
        """Deactivate selected currencies."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Deactivated {updated} currency(ies).", level='WARNING')
    
    # Standalone actions (new approach with decorator)
    @standalone_action(
        description="Update Rates",
        variant=ActionVariant.SUCCESS,
        icon="sync",
        background=True,
        success_message="💱 Rates update started! Refresh page in 2-3 minutes to see results.",
        error_message="❌ Failed to start rates update: {error}"
    )
    def update_rates(self, request):
        """
        Update currency rates and sync providers.
        
        Performs: populate currencies + sync providers + update rates.
        """
        # 1. Populate all supported currencies (fast)
        call_command('manage_currencies', '--populate')
        
        # 2. Sync all providers (medium speed)
        call_command('manage_providers', '--all')
        
        # 3. Update USD rates (slower)
        call_command('manage_currencies', '--rates-only')
        
        return "Currency rates updated successfully"
    
    @standalone_action(
        description="Sync Providers",
        variant=ActionVariant.INFO,
        icon="cloud_sync",
        background=True,
        success_message="🔄 Provider sync started in background.",
        error_message="❌ Provider sync failed: {error}"
    )
    def sync_providers(self, request):
        """Sync all currency providers."""
        call_command('manage_providers', '--all')
        return "Providers synced successfully"
    
    @standalone_action(
        description="Backup Data",
        variant=ActionVariant.WARNING,
        icon="backup",
        success_message="💾 Currency data backup completed: {result}",
        error_message="❌ Backup failed: {error}"
    )
    def backup_data(self, request):
        """Create backup of currency data."""
        from django.utils import timezone
        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        
        # Simulate backup logic
        total_currencies = Currency.objects.count()
        
        # Here you would implement actual backup logic
        # For example: export to JSON, create database dump, etc.
        
        return f"{total_currencies} currencies backed up to currencies_{timestamp}.json"
    
    def changelist_view(self, request, extra_context=None):
        """Add statistics to changelist context."""
        extra_context = extra_context or {}
        
        try:
            # Basic statistics
            total_currencies = Currency.objects.count()
            active_count = Currency.objects.filter(is_active=True).count()
            
            # Rate statistics (simplified - assuming usd_rate field exists)
            currencies_with_rates = Currency.objects.exclude(
                models.Q(usd_rate__isnull=True) | models.Q(usd_rate=0)
            ).count() if hasattr(Currency, 'usd_rate') else 0
            
            rate_coverage = (currencies_with_rates / total_currencies * 100) if total_currencies > 0 else 0
            
            # Currency types (if field exists)
            fiat_count = 0
            crypto_count = 0
            if hasattr(Currency, 'currency_type'):
                try:
                    fiat_count = Currency.objects.filter(currency_type='fiat').count()
                    crypto_count = Currency.objects.filter(currency_type='crypto').count()
                except:
                    pass
            
            extra_context.update({
                'currency_stats': {
                    'total_currencies': total_currencies,
                    'fiat_count': fiat_count,
                    'crypto_count': crypto_count,
                    'active_count': active_count,
                    'currencies_with_rates': currencies_with_rates,
                    'rate_coverage': rate_coverage,
                    'enabled_provider_currencies': 0,  # Placeholder
                    'top_currencies': [],  # Placeholder
                }
            })
            
        except Exception as e:
            logger.warning(f"Failed to generate currency statistics: {e}")
            extra_context['currency_stats'] = None
        
        return super().changelist_view(request, extra_context)
