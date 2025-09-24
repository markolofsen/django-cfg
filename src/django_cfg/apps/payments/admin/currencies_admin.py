"""
Admin interface for currencies.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.contrib.humanize.templatetags.humanize import naturaltime
from unfold.admin import ModelAdmin
from unfold.decorators import display

from ..models import Currency, CurrencyNetwork
from .filters import CurrencyTypeFilter


@admin.register(Currency)
class CurrencyAdmin(ModelAdmin):
    """Admin interface for currencies."""
    
    list_display = [
        'currency_display',
        'type_display',
        'rate_display',
        'status_display',
        'created_at_display'
    ]
    
    list_display_links = ['currency_display']
    
    search_fields = ['code', 'name', 'symbol']
    
    list_filter = [
        CurrencyTypeFilter,
        'is_active',
        'created_at'
    ]
    
    readonly_fields = ['rate_updated_at', 'created_at', 'updated_at']
    
    fieldsets = [
        ('Currency Information', {
            'fields': ['code', 'name', 'symbol', 'currency_type']
        }),
        ('Configuration', {
            'fields': ['decimal_places', 'min_payment_amount', 'is_active']
        }),
        ('Exchange Rate', {
            'fields': ['usd_rate', 'rate_updated_at']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    @display(description="Currency")
    def currency_display(self, obj):
        """Display currency with symbol."""
        return format_html(
            '<strong>{}</strong> {}<br><small>{}</small>',
            obj.code,
            obj.symbol,
            obj.name
        )
    
    @display(description="Type")
    def type_display(self, obj):
        """Display currency type with badge."""
        type_colors = {
            'fiat': '#28a745',
            'crypto': '#fd7e14',
        }
        
        color = type_colors.get(obj.currency_type, '#6c757d')
        
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_currency_type_display()
        )
    
    @display(description="USD Rate")
    def rate_display(self, obj):
        """Display exchange rate."""
        if obj.usd_rate != 1.0:
            return format_html(
                '<strong>1 {} = ${:.6f}</strong><br><small>Updated: {}</small>',
                obj.code,
                obj.usd_rate,
                naturaltime(obj.rate_updated_at) if obj.rate_updated_at else 'Never'
            )
        return format_html('<span style="color: #6c757d;">Base currency</span>')
    
    @display(description="Status")
    def status_display(self, obj):
        """Display status badge."""
        if obj.is_active:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">Active</span>'
            )
        else:
            return format_html(
                '<span style="background: #dc3545; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">Inactive</span>'
            )
    
    @display(description="Created")
    def created_at_display(self, obj):
        """Display creation date."""
        return naturaltime(obj.created_at)


@admin.register(CurrencyNetwork)
class CurrencyNetworkAdmin(ModelAdmin):
    """Admin interface for currency networks."""
    
    list_display = [
        'network_display',
        'currency_display',
        'status_display',
        'confirmations_display',
        'created_at_display'
    ]
    
    list_display_links = ['network_display']
    
    search_fields = ['network_name', 'network_code', 'currency__code', 'currency__name']
    
    list_filter = ['currency', 'is_active', 'created_at']
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ('Network Information', {
            'fields': ['currency', 'network_name', 'network_code']
        }),
        ('Configuration', {
            'fields': ['confirmation_blocks', 'is_active']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    @display(description="Network")
    def network_display(self, obj):
        """Display network information."""
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            obj.network_name,
            obj.network_code
        )
    
    @display(description="Currency")
    def currency_display(self, obj):
        """Display currency information."""
        return format_html(
            '<strong>{}</strong> {}<br><small>{}</small>',
            obj.currency.code,
            obj.currency.symbol,
            obj.currency.name
        )
    
    @display(description="Status")
    def status_display(self, obj):
        """Display status badge."""
        if obj.is_active:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">Active</span>'
            )
        else:
            return format_html(
                '<span style="background: #dc3545; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">Inactive</span>'
            )
    
    @display(description="Confirmations")
    def confirmations_display(self, obj):
        """Display confirmation blocks."""
        return format_html(
            '<span style="font-weight: bold;">{}</span> blocks',
            obj.confirmation_blocks
        )
    
    @display(description="Created")
    def created_at_display(self, obj):
        """Display creation date."""
        return naturaltime(obj.created_at)
