"""
Networks Admin interface using Django Admin Utilities.

Clean network and provider currency management.
"""

from django.contrib import admin
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from unfold.admin import ModelAdmin

from django_cfg.modules.django_admin import (
    OptimizedModelAdmin,
    DisplayMixin,
    UserDisplayConfig,
    StatusBadgeConfig,
    MoneyDisplayConfig,
    DateTimeDisplayConfig,
    Icons,
    display,
    action,
    ActionVariant
)
from django_cfg.modules.django_admin.utils.displays import (
    UserDisplay,
    MoneyDisplay,
    StatusDisplay,
    DateTimeDisplay
)
from django_cfg.modules.django_admin.utils.badges import StatusBadge

from ..models.currencies import Network, ProviderCurrency


@admin.register(Network)
class NetworkAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin):
    """
    Admin interface for Network model.
    
    Features:
    - Network information display
    - Chain ID and explorer links
    - Status management
    - Automatic query optimization
    """
    
    # Performance optimization
    select_related_fields = ['native_currency']
    annotations = {}
    
    # List configuration
    list_display = [
        'name_display',
        'code_display',
        'native_currency_display',
        'explorer_display',
        'status_display',
        'created_at_display'
    ]
    
    list_filter = [
        'is_active',
        'created_at'
    ]
    
    search_fields = ['name', 'code']
    
    readonly_fields = [
        'created_at',
        'updated_at'
    ]
    
    # Display methods
    @display(description="Network", ordering="name")
    def name_display(self, obj):
        """Network name display."""
        return obj.name
    
    @display(description="Code")
    def code_display(self, obj):
        """Network code display."""
        return obj.code
    
    @display(description="Native Currency")
    def native_currency_display(self, obj):
        """Native currency display."""
        if obj.native_currency:
            return f"{obj.native_currency.code} ({obj.native_currency.name})"
        return "—"
    
    @display(description="Explorer")
    def explorer_display(self, obj: Network):
        """Explorer link display."""
        if obj.block_explorer_url:
            return "View Explorer"
        return "—"
    
    @display(description="Status")
    def status_display(self, obj: Network):
        """Status display."""
        if obj.is_active:
            status = "Active"
            variant = "success"
            icon = Icons.CHECK_CIRCLE
        else:
            status = "Inactive"
            variant = "danger"
            icon = Icons.CANCEL
        
        return StatusBadge.create(
            text=status,
            variant=variant,
            icon=icon
        )
    
    @display(description="Created")
    def created_at_display(self, obj: Network):
        """Created at display."""
        config = DateTimeDisplayConfig(
            show_relative=True,
            show_seconds=False
        )
        return self.display_datetime_relative(obj, 'created_at', config)


@admin.register(ProviderCurrency)
class ProviderCurrencyAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin):
    """
    Admin interface for ProviderCurrency model.
    
    Features:
    - Provider and currency relationships
    - Fee and limit display
    - Status management
    """
    
    # Performance optimization
    select_related_fields = ['currency', 'network']
    annotations = {}
    
    # List configuration
    list_display = [
        'currency_display',
        'provider_currency_code_display',
        'network_display',
        'provider_display',
        'fees_display',
        'limits_display',
        'status_display',
        'created_at_display'
    ]
    
    list_filter = [
        'is_enabled',
        'provider',
        'currency__symbol',
        'network__name',
        'created_at'
    ]
    
    search_fields = [
        'currency__name',
        'currency__symbol',
        'network__name',
        'provider',
        'provider_currency_code'
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at'
    ]
    
    # Display methods
    @display(description="Currency")
    def currency_display(self, obj: ProviderCurrency):
        """Currency display."""
        return StatusBadge.create(
            text=f"{obj.currency.symbol} ({obj.currency.name})",
            variant="primary",
            icon=Icons.CURRENCY_BITCOIN
        )
    
    @display(description="Provider Code")
    def provider_currency_code_display(self, obj: ProviderCurrency):
        """Provider currency code display."""
        return StatusBadge.create(
            text=obj.provider_currency_code,
            variant="warning",
            icon=Icons.CODE
        )
    
    @display(description="Network")
    def network_display(self, obj: ProviderCurrency):
        """Network display."""
        if obj.network:
            return StatusBadge.create(
                text=obj.network.name,
                variant="info",
                icon=Icons.LINK
            )
        return "—"
    
    @display(description="Provider")
    def provider_display(self, obj: ProviderCurrency):
        """Provider display."""
        return StatusBadge.create(
            text=obj.provider.title(),
            variant="secondary",
            icon=Icons.PAYMENT
        )
    
    @display(description="Fees")
    def fees_display(self, obj: ProviderCurrency):
        """Fees display."""
        fees = []
        
        if obj.deposit_fee_percentage > 0:
            fees.append(f"Deposit: {obj.deposit_fee_percentage}%")
        
        if obj.withdrawal_fee_percentage > 0:
            fees.append(f"Withdrawal: {obj.withdrawal_fee_percentage}%")
        
        if obj.fixed_fee_usd > 0:
            fees.append(f"Fixed: ${obj.fixed_fee_usd}")
        
        return " • ".join(fees) if fees else "No fees"
    
    @display(description="Limits")
    def limits_display(self, obj: ProviderCurrency):
        """Limits display."""
        limits = []
        
        if obj.min_amount > 0:
            limits.append(f"Min: {obj.min_amount}")
        
        if obj.max_amount > 0:
            limits.append(f"Max: {obj.max_amount}")
        
        return " • ".join(limits) if limits else "No limits"
    
    @display(description="Status")
    def status_display(self, obj: ProviderCurrency):
        """Status display."""
        if obj.is_enabled:
            status = "Enabled"
            variant = "success"
            icon = Icons.CHECK_CIRCLE
        else:
            status = "Disabled"
            variant = "danger"
            icon = Icons.CANCEL
        
        return StatusBadge.create(
            text=status,
            variant=variant,
            icon=icon
        )
    
    @display(description="Created")
    def created_at_display(self, obj: ProviderCurrency):
        """Created at display."""
        config = DateTimeDisplayConfig(
            show_relative=True,
            show_seconds=False
        )
        return self.display_datetime_relative(obj, 'created_at', config)
