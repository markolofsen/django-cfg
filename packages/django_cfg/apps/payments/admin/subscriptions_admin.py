"""
Subscriptions Admin interface using Django Admin Utilities.

Clean subscription management with plan icons and status tracking.
"""

from django.contrib import admin
from django.db.models import Count
from unfold.admin import ModelAdmin

from django_cfg.modules.django_admin import (
    OptimizedModelAdmin,
    DisplayMixin,
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
from ..models import Subscription

logger = get_logger("subscriptions_admin")


@admin.register(Subscription)
class SubscriptionAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin):
    """Subscription admin using Django Admin Utilities with plan icons."""
    
    select_related_fields = ['user']
    
    list_display = [
        'user_display',
        'plan_display',
        'amount_display',
        'status_display',
        'expires_display'
    ]
    
    list_filter = ['status', 'tier', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    # Register actions
    actions = ['activate_subscriptions', 'cancel_subscriptions', 'extend_trial']
    
    @display(description="User", header=True)
    def user_display(self, obj):
        """User display with avatar."""
        return self.display_user_with_avatar(obj, 'user')
    
    @display(description="Plan")
    def plan_display(self, obj):
        """Plan display with tier-specific icons."""
        # Plan type to icon and variant mapping
        plan_config = {
            'basic': {'variant': 'secondary', 'icon': Icons.PERSON},
            'premium': {'variant': 'primary', 'icon': Icons.STAR}, 
            'enterprise': {'variant': 'success', 'icon': Icons.BUSINESS},
            'pro': {'variant': 'info', 'icon': Icons.WORKSPACE_PREMIUM},
        }
        
        tier = getattr(obj, 'tier', '').lower()
        config_data = plan_config.get(tier, {'variant': 'info', 'icon': Icons.SUBSCRIPTIONS})
        
        tier_name = obj.get_tier_display() if hasattr(obj, 'get_tier_display') else obj.tier.title()
        
        badge_config = StatusBadgeConfig(
            show_icons=True,
            icon=config_data['icon']
        )
        
        return StatusBadge.create(
            text=tier_name,
            variant=config_data['variant'],
            config=badge_config
        )
    
    @display(description="Amount")
    def amount_display(self, obj):
        """Amount display with currency."""
        config = MoneyDisplayConfig(currency="USD", show_sign=False)
        return self.display_money_amount(obj, 'monthly_cost_usd', config)
    
    @display(description="Status", label=True)
    def status_display(self, obj):
        """Status display with subscription-specific icons."""
        subscription_mappings = {
            'active': 'success',
            'expired': 'danger',
            'cancelled': 'secondary',
            'pending': 'warning',
            'trial': 'info'
        }
        
        # Status-specific icons
        status_icons = {
            'active': Icons.CHECK_CIRCLE,
            'expired': Icons.SCHEDULE,
            'cancelled': Icons.CANCEL,
            'pending': Icons.PENDING,
            'trial': Icons.TIMER
        }
        
        status = getattr(obj, 'status', 'unknown').lower()
        icon = status_icons.get(status, Icons.HELP)
        
        config = StatusBadgeConfig(
            custom_mappings=subscription_mappings,
            show_icons=True,
            icon=icon
        )
        
        return self.display_status_auto(obj, 'status', config)
    
    @display(description="Expires")
    def expires_display(self, obj):
        """Expiry date display."""
        if not hasattr(obj, 'expires_at') or not obj.expires_at:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.ALL_INCLUSIVE)
            return StatusBadge.create(text="No Expiry", variant="info", config=config)
        
        return self.display_datetime_relative(obj, 'expires_at')
    
    @action(description="Activate subscriptions", variant=ActionVariant.SUCCESS)
    def activate_subscriptions(self, request, queryset):
        """Activate selected subscriptions."""
        updated = queryset.update(status='active')
        self.message_user(request, f"Activated {updated} subscription(s).", level='SUCCESS')
    
    @action(description="Cancel subscriptions", variant=ActionVariant.WARNING)
    def cancel_subscriptions(self, request, queryset):
        """Cancel selected subscriptions."""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f"Cancelled {updated} subscription(s).", level='WARNING')
    
    @action(description="Extend trial period", variant=ActionVariant.INFO)
    def extend_trial(self, request, queryset):
        """Extend trial period for selected subscriptions."""
        from django.utils import timezone
        from datetime import timedelta
        
        trial_subs = queryset.filter(status='trial')
        updated_count = 0
        
        for sub in trial_subs:
            if hasattr(sub, 'expires_at') and sub.expires_at:
                # Extend by 7 days
                sub.expires_at = sub.expires_at + timedelta(days=7)
                sub.save()
                updated_count += 1
        
        self.message_user(
            request,
            f"Extended trial period for {updated_count} subscription(s).",
            level='INFO'
        )
