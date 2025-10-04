"""
Tariffs Admin interface using Django Admin Utilities.

Clean tariff management with pricing and limits display.
"""

from django.contrib import admin
from django.db.models import Count, Q
from django.utils import timezone
from django.utils.html import format_html
from datetime import timedelta

from unfold.admin import ModelAdmin

from django_cfg.modules.django_admin import (
    OptimizedModelAdmin,
    DisplayMixin,
    MoneyDisplayConfig,
    DateTimeDisplayConfig,
    StatusBadgeConfig,
    Icons,
    ActionVariant,
    display,
    action
)
from django_cfg.modules.django_admin.utils.badges import StatusBadge

from ..models.tariffs import Tariff, TariffEndpointGroup


@admin.register(Tariff)
class TariffAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin):
    """
    Admin interface for Tariff model.
    
    Features:
    - Clean pricing display
    - Rate limits visualization
    - Feature flags display
    - Automatic query optimization
    - Type-safe configuration
    """
    
    # Performance optimization
    select_related_fields = []
    annotations = {}
    
    # List configuration
    list_display = [
        'name_display',
        'code_display',
        'pricing_display',
        'rate_limits_display',
        'features_display',
        'status_display',
        'created_at_display'
    ]
    
    list_filter = [
        'is_active',
        'is_public',
        'supports_webhooks',
        'priority_support',
        'created_at'
    ]
    
    search_fields = ['name', 'code', 'description']
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'yearly_discount_percentage'
    ]
    
    # Display methods using Unfold features
    @display(description="Name", ordering="name")
    def name_display(self, obj):
        """Tariff name display."""
        return obj.name
    
    @display(description="Code", ordering="code")
    def code_display(self, obj):
        """Tariff code display."""
        return obj.code
    
    @display(description="Pricing", ordering="monthly_price_usd")
    def pricing_display(self, obj):
        """Pricing display using utilities."""
        monthly = self.display_money_amount(
            obj, 
            'monthly_price_usd',
            MoneyDisplayConfig(currency="USD", show_sign=False)
        )
        
        if obj.yearly_price_usd:
            yearly = self.display_money_amount(
                obj,
                'yearly_price_usd', 
                MoneyDisplayConfig(currency="USD", show_sign=False)
            )
            discount = f"{obj.yearly_discount_percentage:.0f}% off"
            return format_html("{}/mo • {}/yr ({})", monthly, yearly, discount)
        
        return format_html("{}/mo", monthly)
    
    @display(description="Rate Limits")
    def rate_limits_display(self, obj):
        """Rate limits display."""
        return f"{obj.requests_per_hour:,}/hr • {obj.requests_per_day:,}/day • {obj.requests_per_month:,}/mo"
    
    @display(description="Features")
    def features_display(self, obj):
        """Features display."""
        features = []
        
        features.append(f"{obj.max_api_keys} API keys")
        
        if obj.supports_webhooks:
            features.append("Webhooks")
        
        if obj.priority_support:
            features.append("Priority Support")
        
        return " • ".join(features)
    
    @display(description="Status", label={
        "Active": "success",
        "Private": "warning", 
        "Inactive": "danger"
    })
    def status_display(self, obj):
        """Status display using Unfold label feature."""
        if obj.is_active and obj.is_public:
            return "Active"
        elif obj.is_active:
            return "Private"
        else:
            return "Inactive"
    
    @display(description="Created")
    def created_at_display(self, obj):
        """Created at display."""
        config = DateTimeDisplayConfig(
            show_relative=True,
            show_seconds=False
        )
        return self.display_datetime_relative(obj, 'created_at', config)


@admin.register(TariffEndpointGroup)
class TariffEndpointGroupAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin):
    """
    Admin interface for TariffEndpointGroup model.
    
    Features:
    - Tariff and endpoint group relationships
    - Custom rate limit display
    - Clean utilities integration
    """
    
    # Performance optimization
    select_related_fields = ['tariff', 'endpoint_group']
    annotations = {}
    
    # List configuration
    list_display = [
        'tariff_display',
        'endpoint_group_display',
        'rate_limit_display',
        'status_display',
        'created_at_display'
    ]
    
    list_filter = [
        'is_enabled',
        'tariff__is_active',
        'created_at'
    ]
    
    search_fields = [
        'tariff__name',
        'endpoint_group__name'
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'effective_rate_limit'
    ]
    
    # Display methods
    @display(description="Tariff")
    def tariff_display(self, obj):
        """Tariff display."""
        config = StatusBadgeConfig(show_icons=True, icon=Icons.PRICE_CHANGE)
        return StatusBadge.create(
            text=obj.tariff.name,
            variant="primary",
            config=config
        )
    
    @display(description="Endpoint Group")
    def endpoint_group_display(self, obj):
        """Endpoint group display."""
        config = StatusBadgeConfig(show_icons=True, icon=Icons.GROUP)
        return StatusBadge.create(
            text=obj.endpoint_group.name,
            variant="info",
            config=config
        )
    
    @display(description="Rate Limit")
    def rate_limit_display(self, obj):
        """Rate limit display."""
        effective = obj.effective_rate_limit
        
        if obj.custom_rate_limit:
            return f"{effective:,}/hr (custom)"
        else:
            return f"{effective:,}/hr (default)"
    
    @display(description="Status")
    def status_display(self, obj):
        """Status display."""
        if obj.is_enabled:
            status = "Enabled"
            variant = "success"
            icon = Icons.CHECK_CIRCLE
        else:
            status = "Disabled"
            variant = "danger"
            icon = Icons.CANCEL
        
        config = StatusBadgeConfig(show_icons=True, icon=icon)
        return StatusBadge.create(
            text=status,
            variant=variant,
            config=config
        )
    
    @display(description="Created")
    def created_at_display(self, obj):
        """Created at display."""
        config = DateTimeDisplayConfig(
            show_relative=True,
            show_seconds=False
        )
        return self.display_datetime_relative(obj, 'created_at', config)
