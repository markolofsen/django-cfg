"""
Subscription Admin interfaces with Unfold integration.

Advanced subscription lifecycle management and monitoring.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from typing import Optional

from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display, action
from unfold.enums import ActionVariant

from ..models import Subscription, EndpointGroup, Tariff, TariffEndpointGroup
from .filters import SubscriptionTierFilter, SubscriptionStatusFilter, RecentActivityFilter
from django_cfg.modules.django_logger import get_logger

logger = get_logger("subscriptions_admin")


class TariffEndpointGroupInline(TabularInline):
    """Inline for tariff endpoint groups."""
    model = TariffEndpointGroup
    extra = 0
    fields = ['endpoint_group', 'custom_rate_limit', 'is_enabled']


@admin.register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    """
    Advanced Subscription admin with lifecycle management.
    
    Features:
    - Subscription lifecycle tracking
    - Usage monitoring and alerts
    - Bulk subscription operations
    - Expiration management
    - Tier-based filtering and actions
    """
    
    # Custom template for subscription statistics
    change_list_template = 'admin/payments/subscription/change_list.html'
    
    list_display = [
        'subscription_display',
        'user_display',
        'tier_display',
        'status_display',
        'usage_display',
        'expiry_display',
        'created_at_display'
    ]
    
    list_display_links = ['subscription_display']
    
    search_fields = [
        'id',
        'user__email',
        'user__username',
        'tier'
    ]
    
    list_filter = [
        SubscriptionStatusFilter,
        SubscriptionTierFilter,
        RecentActivityFilter,
        'created_at',
        'expires_at'
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'last_request_at'
    ]
    
    # Unfold actions
    actions_list = [
        'activate_subscriptions',
        'suspend_subscriptions',
        'extend_subscriptions',
    ]
    
    fieldsets = [
        ('Subscription Information', {
            'fields': [
                'id',
                'user',
                'tier',
                'status'
            ]
        }),
        ('Usage & Limits', {
            'fields': [
                'total_requests',
                'requests_per_hour',
                'requests_per_day',
                'last_request_at'
            ]
        }),
        ('Billing & Expiry', {
            'fields': [
                'monthly_cost_usd',
                'starts_at',
                'expires_at',
                'auto_renew'
            ]
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related('user').prefetch_related('endpoint_groups')
    
    @display(description="Subscription", ordering='id')
    def subscription_display(self, obj):
        """Display subscription ID with tier indicator."""
        short_id = str(obj.id)[:8]
        
        tier_icons = {
            'free': '🆓',
            'basic': '🥉',
            'pro': '🥈',
            'enterprise': '🥇'
        }
        
        tier_icon = tier_icons.get(obj.tier, '📋')
        
        return format_html(
            '<div class="flex items-center space-x-2">'
            '<span class="text-lg">{}</span>'
            '<span class="font-mono text-sm bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded" title="Full ID: {}">{}</span>'
            '</div>',
            tier_icon,
            obj.id,
            short_id
        )
    
    @display(description="User", ordering='user__email')
    def user_display(self, obj):
        """Display user information with subscription history."""
        if obj.user:
            # Count user's total subscriptions
            total_subscriptions = Subscription.objects.filter(user=obj.user).count()
            
            return format_html(
                '<div>'
                '<div class="font-medium text-gray-900 dark:text-gray-100">{}</div>'
                '<div class="text-xs text-gray-500">{}</div>'
                '<div class="text-xs text-blue-600 dark:text-blue-400">{} subscription{}</div>'
                '</div>',
                obj.user.get_full_name() or obj.user.username,
                obj.user.email,
                total_subscriptions,
                's' if total_subscriptions != 1 else ''
            )
        return format_html('<span class="text-gray-500">No user</span>')
    
    @display(description="Tier", ordering='tier')
    def tier_display(self, obj):
        """Display subscription tier with pricing."""
        tier_colors = {
            'free': 'text-gray-600 dark:text-gray-400',
            'basic': 'text-yellow-600 dark:text-yellow-400',
            'pro': 'text-blue-600 dark:text-blue-400',
            'enterprise': 'text-purple-600 dark:text-purple-400'
        }
        
        color = tier_colors.get(obj.tier, 'text-gray-600')
        
        return format_html(
            '<div>'
            '<div class="font-medium {}">{}</div>'
            '<div class="text-xs text-gray-500">${}/month</div>'
            '</div>',
            color,
            obj.get_tier_display(),
            obj.monthly_cost_usd
        )
    
    @display(description="Status", ordering='status')
    def status_display(self, obj):
        """Display status with expiry warnings."""
        status_config = {
            Subscription.SubscriptionStatus.ACTIVE: ('✅', 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200', 'Active'),
            Subscription.SubscriptionStatus.EXPIRED: ('⌛', 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200', 'Expired'),
            Subscription.SubscriptionStatus.CANCELLED: ('🚫', 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200', 'Cancelled'),
            Subscription.SubscriptionStatus.SUSPENDED: ('⏸️', 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200', 'Suspended'),
        }
        
        icon, color_class, label = status_config.get(
            obj.status,
            ('❓', 'bg-gray-100 text-gray-800', 'Unknown')
        )
        
        badge = format_html(
            '<span class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium {}">'
            '{} {}'
            '</span>',
            color_class,
            icon,
            label
        )
        
        # Add expiry warning if active and expiring soon
        if obj.status == Subscription.SubscriptionStatus.ACTIVE and obj.expires_at:
            time_until_expiry = obj.expires_at - timezone.now()
            if time_until_expiry < timedelta(days=7):
                warning = format_html(
                    '<div class="text-xs text-orange-600 dark:text-orange-400 mt-1">⚠️ Expires soon</div>'
                )
                return format_html('{}<br>{}', badge, warning)
        
        return badge
    
    @display(description="Usage")
    def usage_display(self, obj):
        """Display usage statistics with progress bars."""
        monthly_limit = obj.requests_per_day * 30  # Approximate monthly limit
        monthly_used = obj.total_requests
        
        if monthly_limit > 0:
            usage_percentage = (monthly_used / monthly_limit) * 100
            
            if usage_percentage >= 90:
                bar_color = "bg-red-500"
                text_color = "text-red-600 dark:text-red-400"
            elif usage_percentage >= 75:
                bar_color = "bg-orange-500"
                text_color = "text-orange-600 dark:text-orange-400"
            else:
                bar_color = "bg-green-500"
                text_color = "text-green-600 dark:text-green-400"
            
            return format_html(
                '<div class="w-full">'
                '<div class="flex justify-between text-xs {}">'
                '<span>{:,} / {:,}</span>'
                '<span>{:.1f}%</span>'
                '</div>'
                '<div class="w-full bg-gray-200 rounded-full h-2 dark:bg-gray-700 mt-1">'
                '<div class="{} h-2 rounded-full" style="width: {}%"></div>'
                '</div>'
                '</div>',
                text_color,
                monthly_used,
                monthly_limit,
                usage_percentage,
                bar_color,
                min(usage_percentage, 100)
            )
        else:
            # Unlimited plan
            return format_html(
                '<div class="text-center">'
                '<div class="font-bold text-blue-600 dark:text-blue-400">{:,}</div>'
                '<div class="text-xs text-gray-500">Total requests</div>'
                '</div>',
                monthly_used
            )
    
    @display(description="Expiry", ordering='expires_at')
    def expiry_display(self, obj):
        """Display expiry information with countdown."""
        if not obj.expires_at:
            return format_html(
                '<div class="text-center text-blue-600 dark:text-blue-400">'
                '<div class="font-bold">∞</div>'
                '<div class="text-xs">Never expires</div>'
                '</div>'
            )
        
        now = timezone.now()
        
        if obj.expires_at <= now:
            # Already expired
            return format_html(
                '<div class="text-center text-red-600 dark:text-red-400">'
                '<div class="font-bold">Expired</div>'
                '<div class="text-xs">{}</div>'
                '</div>',
                naturaltime(obj.expires_at)
            )
        
        time_remaining = obj.expires_at - now
        
        if time_remaining < timedelta(days=1):
            color = "text-red-600 dark:text-red-400"
            icon = "🚨"
        elif time_remaining < timedelta(days=7):
            color = "text-orange-600 dark:text-orange-400"
            icon = "⚠️"
        else:
            color = "text-green-600 dark:text-green-400"
            icon = "✅"
        
        return format_html(
            '<div class="text-center {}">'
            '<div><span class="mr-1">{}</span>{}</div>'
            '<div class="text-xs">{}</div>'
            '</div>',
            color,
            icon,
            naturaltime(obj.expires_at),
            obj.expires_at.strftime('%Y-%m-%d')
        )
    
    @display(description="Created", ordering='created_at')
    def created_at_display(self, obj):
        """Display creation date."""
        return format_html(
            '<div class="text-xs">'
            '<div>{}</div>'
            '<div class="text-gray-500">{}</div>'
            '</div>',
            obj.created_at.strftime('%Y-%m-%d'),
            naturaltime(obj.created_at)
        )
    
    def changelist_view(self, request, extra_context=None):
        """Add subscription statistics to changelist context."""
        extra_context = extra_context or {}
        
        try:
            # Basic statistics
            total_subscriptions = Subscription.objects.count()
            
            # Status distribution
            status_stats = {}
            for status in Subscription.SubscriptionStatus:
                count = Subscription.objects.filter(status=status).count()
                status_stats[status] = count
            
            # Tier distribution
            tier_stats = Subscription.objects.values('tier').annotate(
                count=Count('id')
            ).order_by('tier')
            
            # Revenue statistics
            revenue_stats = Subscription.objects.filter(
                status=Subscription.SubscriptionStatus.ACTIVE
            ).values('tier').annotate(
                count=Count('id'),
                revenue=Sum('monthly_cost_usd')
            )
            
            # Expiry alerts
            now = timezone.now()
            expiring_soon = Subscription.objects.filter(
                status=Subscription.SubscriptionStatus.ACTIVE,
                expires_at__lte=now + timedelta(days=7),
                expires_at__gt=now
            ).count()
            
            recently_expired = Subscription.objects.filter(
                status=Subscription.SubscriptionStatus.EXPIRED,
                expires_at__gte=now - timedelta(days=7)
            ).count()
            
            # Usage statistics
            high_usage_subscriptions = Subscription.objects.filter(
                status=Subscription.SubscriptionStatus.ACTIVE,
                total_requests__gte=1000
            ).count()
            
            extra_context.update({
                'subscription_stats': {
                    'total_subscriptions': total_subscriptions,
                    'status_stats': status_stats,
                    'tier_stats': tier_stats,
                    'revenue_stats': revenue_stats,
                    'expiring_soon': expiring_soon,
                    'recently_expired': recently_expired,
                    'high_usage_subscriptions': high_usage_subscriptions,
                }
            })
            
        except Exception as e:
            logger.warning(f"Failed to generate subscription statistics: {e}")
            extra_context['subscription_stats'] = None
        
        return super().changelist_view(request, extra_context)
    
    # ===== ADMIN ACTIONS =====
    
    @action(
        description="✅ Activate Subscriptions",
        icon="play_arrow",
        variant=ActionVariant.SUCCESS
    )
    def activate_subscriptions(self, request, queryset):
        """Activate selected subscriptions."""
        
        activatable = queryset.filter(
            status__in=[
                Subscription.SubscriptionStatus.SUSPENDED,
                Subscription.SubscriptionStatus.CANCELLED
            ]
        )
        
        activated_count = 0
        
        for subscription in activatable:
            try:
                subscription.activate()
                activated_count += 1
                
            except Exception as e:
                logger.error(f"Failed to activate subscription {subscription.id}: {e}")
        
        if activated_count > 0:
            messages.success(
                request,
                f"✅ Activated {activated_count} subscriptions"
            )
        
        skipped = queryset.count() - activated_count
        if skipped > 0:
            messages.info(
                request,
                f"ℹ️ Skipped {skipped} subscriptions (already active or expired)"
            )
    
    @action(
        description="⏸️ Suspend Subscriptions",
        icon="pause",
        variant=ActionVariant.WARNING
    )
    def suspend_subscriptions(self, request, queryset):
        """Suspend selected subscriptions."""
        
        suspendable = queryset.filter(
            status=Subscription.SubscriptionStatus.ACTIVE
        )
        
        suspended_count = 0
        
        for subscription in suspendable:
            try:
                subscription.suspend(reason=f"Suspended by admin {request.user.username}")
                suspended_count += 1
                
            except Exception as e:
                logger.error(f"Failed to suspend subscription {subscription.id}: {e}")
        
        if suspended_count > 0:
            messages.success(
                request,
                f"⏸️ Suspended {suspended_count} subscriptions"
            )
        
        skipped = queryset.count() - suspended_count
        if skipped > 0:
            messages.info(
                request,
                f"ℹ️ Skipped {skipped} subscriptions (not active)"
            )
    
    @action(
        description="📅 Extend Subscriptions (30 days)",
        icon="schedule",
        variant=ActionVariant.INFO
    )
    def extend_subscriptions(self, request, queryset):
        """Extend selected subscriptions by 30 days."""
        
        extendable = queryset.filter(
            status__in=[
                Subscription.SubscriptionStatus.ACTIVE,
                Subscription.SubscriptionStatus.EXPIRED
            ]
        )
        
        extended_count = 0
        
        for subscription in extendable:
            try:
                subscription.renew(duration_days=30)
                extended_count += 1
                
            except Exception as e:
                logger.error(f"Failed to extend subscription {subscription.id}: {e}")
        
        if extended_count > 0:
            messages.success(
                request,
                f"📅 Extended {extended_count} subscriptions by 30 days"
            )
        
        skipped = queryset.count() - extended_count
        if skipped > 0:
            messages.info(
                request,
                f"ℹ️ Skipped {skipped} subscriptions (cancelled or suspended)"
            )


@admin.register(EndpointGroup)
class EndpointGroupAdmin(ModelAdmin):
    """Admin interface for endpoint groups."""
    
    list_display = [
        'name',
        'description',
        'tariff_count_display',
        'created_at_display'
    ]
    
    search_fields = ['name', 'description']
    
    readonly_fields = ['created_at', 'updated_at']
    
    @display(description="Tariffs")
    def tariff_count_display(self, obj):
        """Display tariff count."""
        count = obj.tariffendpointgroup_set.count()
        return format_html(
            '<span class="inline-flex items-center rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-800 dark:bg-blue-900 dark:text-blue-200">'
            '{} tariff{}'
            '</span>',
            count,
            's' if count != 1 else ''
        )
    
    @display(description="Created", ordering='created_at')
    def created_at_display(self, obj):
        """Display creation date."""
        return naturaltime(obj.created_at)


@admin.register(Tariff)
class TariffAdmin(ModelAdmin):
    """Admin interface for tariffs with endpoint group management."""
    
    list_display = [
        'name',
        'tier_display',
        'price_display',
        'endpoint_groups_display',
        'subscription_count_display',
        'is_active'
    ]
    
    list_filter = ['is_active', 'is_public', 'created_at']
    
    search_fields = ['name', 'description']
    
    readonly_fields = ['created_at', 'updated_at']
    
    inlines = [TariffEndpointGroupInline]
    
    @display(description="Tier", ordering='tier')
    def tier_display(self, obj):
        """Display tier with badge."""
        tier_config = {
            'free': ('🆓', 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'),
            'basic': ('🥉', 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'),
            'premium': ('🥈', 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'),
            'enterprise': ('🥇', 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'),
        }
        
        icon, color_class = tier_config.get(obj.tier, ('📋', 'bg-gray-100 text-gray-800'))
        
        return format_html(
            '<span class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium {}">'
            '{} {}'
            '</span>',
            color_class,
            icon,
            obj.tier.title()
        )
    
    @display(description="Price", ordering='monthly_price_usd')
    def price_display(self, obj):
        """Display price with formatting."""
        if obj.monthly_price_usd == 0:
            return format_html(
                '<span class="font-bold text-green-600 dark:text-green-400">FREE</span>'
            )
        else:
            return format_html(
                '<span class="font-bold text-blue-600 dark:text-blue-400">${}/month</span>',
                obj.monthly_price_usd
            )
    
    @display(description="Endpoint Groups")
    def endpoint_groups_display(self, obj):
        """Display endpoint groups count."""
        count = obj.endpoint_groups.count()
        return format_html(
            '<span class="inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800 dark:bg-green-900 dark:text-green-200">'
            '{} group{}'
            '</span>',
            count,
            's' if count != 1 else ''
        )
    
    @display(description="Subscriptions")
    def subscription_count_display(self, obj):
        """Display active subscription count."""
        count = obj.subscription_set.filter(
            status=Subscription.SubscriptionStatus.ACTIVE
        ).count()
        
        if count > 0:
            return format_html(
                '<span class="inline-flex items-center rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-800 dark:bg-blue-900 dark:text-blue-200">'
                '{} active'
                '</span>',
                count
            )
        
        return format_html(
            '<span class="text-gray-500">No active</span>'
        )


@admin.register(TariffEndpointGroup)
class TariffEndpointGroupAdmin(ModelAdmin):
    """Admin interface for tariff endpoint group relationships."""
    
    list_display = [
        'tariff_display',
        'endpoint_group_display',
        'custom_rate_limit_display',
        'is_enabled'
    ]
    
    list_filter = ['is_enabled', 'endpoint_group']
    
    search_fields = [
        'tariff__name',
        'endpoint_group__name'
    ]
    
    @display(description="Tariff", ordering='tariff__name')
    def tariff_display(self, obj):
        """Display tariff with tier."""
        return format_html(
            '<div>'
            '<div class="font-medium">{}</div>'
            '<div class="text-xs text-gray-500">${}/month</div>'
            '</div>',
            obj.tariff.name,
            obj.tariff.monthly_price_usd
        )
    
    @display(description="Endpoint Group", ordering='endpoint_group__name')
    def endpoint_group_display(self, obj):
        """Display endpoint group."""
        return obj.endpoint_group.name
    
    @display(description="Custom Rate Limit", ordering='custom_rate_limit')
    def custom_rate_limit_display(self, obj):
        """Display custom rate limit."""
        if obj.custom_rate_limit:
            return format_html(
                '<span class="font-mono text-orange-600 dark:text-orange-400">{:,}/hour</span>',
                obj.custom_rate_limit
            )
        else:
            return format_html(
                '<span class="text-gray-500">Use tariff default</span>'
            )
