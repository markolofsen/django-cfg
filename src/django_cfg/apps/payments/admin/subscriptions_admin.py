"""
Admin interface for subscriptions.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.contrib.humanize.templatetags.humanize import naturaltime
from unfold.admin import ModelAdmin
from unfold.decorators import display

from ..models import Subscription, EndpointGroup
from .filters import SubscriptionStatusFilter, SubscriptionTierFilter, UsageExceededFilter, UserEmailFilter


@admin.register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    """Admin interface for subscriptions."""
    
    list_display = [
        'subscription_display',
        'user_display',
        'endpoint_group_display',
        'tier_display',
        'status_display',
        'usage_display',
        'expires_display'
    ]
    
    list_display_links = ['subscription_display']
    
    search_fields = [
        'user__email',
        'endpoint_group__name',
        'endpoint_group__display_name'
    ]
    
    list_filter = [
        SubscriptionStatusFilter,
        SubscriptionTierFilter,
        UsageExceededFilter,
        UserEmailFilter,
        'endpoint_group',
        'created_at'
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at'
    ]
    
    fieldsets = [
        ('Subscription Information', {
            'fields': ['user', 'endpoint_group', 'tier', 'status']
        }),
        ('Billing', {
            'fields': ['monthly_price', 'last_billed', 'next_billing']
        }),
        ('Usage', {
            'fields': ['usage_limit', 'usage_current']
        }),
        ('Dates', {
            'fields': ['expires_at', 'cancelled_at', 'created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    @display(description="Subscription")
    def subscription_display(self, obj):
        """Display subscription info."""
        return format_html(
            '<strong>#{}</strong><br><small>{}</small>',
            str(obj.id)[:8],
            obj.endpoint_group.display_name
        )
    
    @display(description="User")
    def user_display(self, obj):
        """Display user information."""
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            obj.user.get_full_name() or obj.user.email,
            obj.user.email
        )
    
    @display(description="Endpoint Group")
    def endpoint_group_display(self, obj):
        """Display endpoint group."""
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            obj.endpoint_group.display_name,
            obj.endpoint_group.description[:40] + '...' if len(obj.endpoint_group.description) > 40 else obj.endpoint_group.description
        )
    
    @display(description="Tier")
    def tier_display(self, obj):
        """Display tier with price."""
        tier_colors = {
            'basic': '#28a745',
            'premium': '#ffc107',
            'enterprise': '#dc3545',
        }
        
        color = tier_colors.get(obj.tier, '#6c757d')
        
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span><br><small>${:.2f}/month</small>',
            color,
            obj.get_tier_display(),
            obj.monthly_price
        )
    
    @display(description="Status")
    def status_display(self, obj):
        """Display status with color coding."""
        status_colors = {
            'active': '#28a745',
            'inactive': '#6c757d',
            'cancelled': '#dc3545',
            'expired': '#fd7e14',
            'trial': '#17a2b8',
        }
        
        color = status_colors.get(obj.status, '#6c757d')
        
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    
    @display(description="Usage")
    def usage_display(self, obj):
        """Display usage with progress."""
        if obj.usage_limit == 0:
            return format_html('<span style="color: #28a745;">Unlimited</span>')
        
        percentage = (obj.usage_current / obj.usage_limit) * 100 if obj.usage_limit > 0 else 0
        
        if percentage >= 100:
            color = '#dc3545'
        elif percentage >= 80:
            color = '#ffc107'
        else:
            color = '#28a745'
        
        return format_html(
            '<span style="color: {};">{}/{}</span><br><small>{:.1f}%</small>',
            color,
            obj.usage_current,
            obj.usage_limit,
            percentage
        )
    
    @display(description="Expires")
    def expires_display(self, obj):
        """Display expiration date."""
        if obj.expires_at:
            return naturaltime(obj.expires_at)
        return '—'


@admin.register(EndpointGroup)
class EndpointGroupAdmin(ModelAdmin):
    """Admin interface for endpoint groups."""
    
    list_display = [
        'name',
        'display_name',
        'pricing_display',
        'limits_display',
        'is_active',
        'created_at_display'
    ]
    
    list_display_links = ['name', 'display_name']
    
    search_fields = ['name', 'display_name', 'description']
    
    list_filter = ['is_active', 'require_api_key', 'created_at']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['name', 'display_name', 'description']
        }),
        ('Pricing Tiers', {
            'fields': ['basic_price', 'premium_price', 'enterprise_price']
        }),
        ('Usage Limits', {
            'fields': ['basic_limit', 'premium_limit', 'enterprise_limit']
        }),
        ('Settings', {
            'fields': ['is_active', 'require_api_key']
        })
    ]
    
    @display(description="Pricing")
    def pricing_display(self, obj):
        """Display pricing tiers."""
        return format_html(
            '<div style="line-height: 1.4;">'
            'Basic: <strong>${:.2f}</strong><br>'
            'Premium: <strong>${:.2f}</strong><br>'
            'Enterprise: <strong>${:.2f}</strong>'
            '</div>',
            obj.basic_price,
            obj.premium_price,
            obj.enterprise_price
        )
    
    @display(description="Limits")
    def limits_display(self, obj):
        """Display usage limits."""
        return format_html(
            '<div style="line-height: 1.4;">'
            'Basic: <strong>{:,}</strong><br>'
            'Premium: <strong>{:,}</strong><br>'
            'Enterprise: <strong>{:,}</strong>'
            '</div>',
            obj.basic_limit,
            obj.premium_limit,
            obj.enterprise_limit if obj.enterprise_limit > 0 else '∞'
        )
    
    @display(description="Created")
    def created_at_display(self, obj):
        """Display creation date."""
        return naturaltime(obj.created_at)
