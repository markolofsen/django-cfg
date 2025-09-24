"""
Admin interface for tariffs.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.contrib.humanize.templatetags.humanize import naturaltime
from unfold.admin import ModelAdmin
from unfold.decorators import display

from ..models import Tariff, TariffEndpointGroup


@admin.register(Tariff)
class TariffAdmin(ModelAdmin):
    """Admin interface for tariffs."""
    
    list_display = [
        'tariff_display',
        'price_display',
        'limit_display',
        'status_display',
        'endpoint_groups_count',
        'created_at_display'
    ]
    
    list_display_links = ['tariff_display']
    
    search_fields = ['name', 'display_name', 'description']
    
    list_filter = ['is_active', 'created_at']
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ('Tariff Information', {
            'fields': ['name', 'display_name', 'description']
        }),
        ('Pricing & Limits', {
            'fields': ['monthly_price', 'request_limit']
        }),
        ('Settings', {
            'fields': ['is_active']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    @display(description="Tariff")
    def tariff_display(self, obj):
        """Display tariff name and description."""
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            obj.display_name,
            obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
        )
    
    @display(description="Price")
    def price_display(self, obj):
        """Display price with free indicator."""
        if obj.monthly_price == 0:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">FREE</span>'
            )
        else:
            return format_html(
                '<strong>${:.2f}</strong>/month',
                obj.monthly_price
            )
    
    @display(description="Request Limit")
    def limit_display(self, obj):
        """Display request limit."""
        if obj.request_limit == 0:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">Unlimited</span>'
            )
        else:
            return format_html(
                '<strong>{:,}</strong>/month',
                obj.request_limit
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
    
    @display(description="Endpoint Groups")
    def endpoint_groups_count(self, obj):
        """Display count of endpoint groups."""
        count = obj.endpoint_groups.filter(is_enabled=True).count()
        total = obj.endpoint_groups.count()
        
        if total == 0:
            return format_html('<span style="color: #6c757d;">No groups</span>')
        
        return format_html(
            '<strong>{}</strong> active<br><small>{} total</small>',
            count,
            total
        )
    
    @display(description="Created")
    def created_at_display(self, obj):
        """Display creation date."""
        return naturaltime(obj.created_at)


@admin.register(TariffEndpointGroup)
class TariffEndpointGroupAdmin(ModelAdmin):
    """Admin interface for tariff endpoint group associations."""
    
    list_display = [
        'association_display',
        'tariff_display',
        'endpoint_group_display',
        'status_display',
        'created_at_display'
    ]
    
    list_display_links = ['association_display']
    
    search_fields = [
        'tariff__name',
        'tariff__display_name',
        'endpoint_group__name',
        'endpoint_group__display_name'
    ]
    
    list_filter = ['is_enabled', 'tariff', 'endpoint_group', 'created_at']
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ('Association', {
            'fields': ['tariff', 'endpoint_group', 'is_enabled']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    @display(description="Association")
    def association_display(self, obj):
        """Display association ID."""
        return format_html(
            '<strong>#{}</strong><br><small>{} → {}</small>',
            str(obj.id)[:8],
            obj.tariff.name,
            obj.endpoint_group.name
        )
    
    @display(description="Tariff")
    def tariff_display(self, obj):
        """Display tariff information."""
        price_text = 'FREE' if obj.tariff.monthly_price == 0 else f'${obj.tariff.monthly_price:.2f}/mo'
        
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            obj.tariff.display_name,
            price_text
        )
    
    @display(description="Endpoint Group")
    def endpoint_group_display(self, obj):
        """Display endpoint group information."""
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            obj.endpoint_group.display_name,
            obj.endpoint_group.description[:30] + '...' if len(obj.endpoint_group.description) > 30 else obj.endpoint_group.description
        )
    
    @display(description="Status")
    def status_display(self, obj):
        """Display status badge."""
        if obj.is_enabled:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">Enabled</span>'
            )
        else:
            return format_html(
                '<span style="background: #dc3545; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">Disabled</span>'
            )
    
    @display(description="Created")
    def created_at_display(self, obj):
        """Display creation date."""
        return naturaltime(obj.created_at)
