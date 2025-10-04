"""
Payment Admin interface using Django Admin Utilities.

Clean, modern payment management with no HTML duplication.
"""

from django.contrib import admin
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta

from unfold.admin import ModelAdmin

from django_cfg.modules.django_admin import (
    OptimizedModelAdmin,
    DisplayMixin,
    UserDisplayConfig,
    MoneyDisplayConfig,
    StatusBadgeConfig,
    DateTimeDisplayConfig,
    Icons,
    display,
    action,
    ActionVariant
)
from django_cfg.modules.django_admin.utils.badges import StatusBadge
from django_cfg.modules.django_logging import get_logger

from ..models import UniversalPayment

logger = get_logger("payments_admin")


@admin.register(UniversalPayment)
class UniversalPaymentAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin):
    """
    UniversalPayment admin using Django Admin Utilities.
    
    Features:
    - Clean display utilities with no HTML duplication
    - Automatic query optimization
    - Type-safe configuration
    - Payment-specific status mapping
    """
    
    # Performance optimization
    select_related_fields = ['user', 'currency']
    annotations = {}
    # Note: Annotations should use Django expressions like F(), Case(), etc.
    # Example: 'age_days': timezone.now() - F('created_at')
    
    # List configuration
    list_display = [
        'payment_id_display',
        'user_display',
        'amount_display',
        'status_display',
        'provider_display',
        'status_changed_display',
        'created_display'
    ]
    
    list_filter = [
        'status',
        'provider',
        'currency',
        'created_at'
    ]
    
    search_fields = [
        'internal_payment_id',
        'transaction_hash',
        'user__username',
        'user__email',
        'pay_address'
    ]
    
    readonly_fields = [
        'internal_payment_id',
        'created_at',
        'updated_at',
        'status_changed_at',
        'payment_details_display'
    ]
    
    # Register actions
    actions = ['mark_as_completed', 'mark_as_failed', 'cancel_payments']
    
    # Display methods using utilities
    @display(description="Payment ID")
    def payment_id_display(self, obj):
        """Payment ID display with badge."""
        return StatusBadge.create(
            text=obj.internal_payment_id[:12] + "...",
            variant="info"
        )
    
    @display(description="User", header=True)
    def user_display(self, obj):
        """User display with avatar."""
        return self.display_user_with_avatar(obj, 'user')
    
    @display(description="Amount")
    def amount_display(self, obj):
        """Amount display with currency."""
        # Get currency code from currency relation or default to USD
        currency_code = "USD"
        if obj.currency:
            currency_code = getattr(obj.currency, 'code', 'USD')
        
        config = MoneyDisplayConfig(
            currency=currency_code,
            show_sign=False,
            thousand_separator=True
        )
        
        return self.display_money_amount(obj, 'amount_usd', config)
    
    @display(description="Status", label=True)
    def status_display(self, obj):
        """Status display with payment-specific colors."""
        # Payment-specific status mappings
        payment_status_mappings = {
            'pending': 'warning',
            'processing': 'info', 
            'completed': 'success',
            'failed': 'danger',
            'cancelled': 'secondary',
            'expired': 'danger',
            'refunded': 'warning'
        }
        
        config = StatusBadgeConfig(
            custom_mappings=payment_status_mappings,
            show_icons=True
        )
        
        return self.display_status_auto(obj, 'status', config)
    
    @display(description="Provider")
    def provider_display(self, obj):
        """Provider display with badge and icons."""
        # Provider-specific styling and icons
        provider_config = {
            'stripe': {'variant': 'primary', 'icon': Icons.CREDIT_CARD},
            'paypal': {'variant': 'info', 'icon': Icons.ACCOUNT_BALANCE_WALLET},
            'crypto': {'variant': 'warning', 'icon': Icons.CURRENCY_BITCOIN},
            'bank': {'variant': 'success', 'icon': Icons.ACCOUNT_BALANCE},
        }
        
        config = provider_config.get(obj.provider.lower(), {'variant': 'secondary', 'icon': Icons.PAYMENT})
        
        badge_config = StatusBadgeConfig(
            show_icons=True,
            icon=config['icon']
        )
        
        return StatusBadge.create(
            text=obj.provider.title(),
            variant=config['variant'],
            config=badge_config
        )
    
    @display(description="Created")
    def created_display(self, obj):
        """Created time display."""
        return self.display_datetime_relative(
            obj,
            'created_at',
            DateTimeDisplayConfig(show_relative=True, show_seconds=False)
        )
    
    @display(description="Status Changed")
    def status_changed_display(self, obj):
        """Status changed time display."""
        if not obj.status_changed_at:
            return "-"
        return self.display_datetime_relative(
            obj,
            'status_changed_at',
            DateTimeDisplayConfig(show_relative=True, show_seconds=False)
        )
    
    # Readonly field displays
    def payment_details_display(self, obj):
        """Detailed payment information for detail view."""
        if not obj.pk:
            return "Save to see details"
        
        from django.utils.html import format_html
        from django_cfg.modules.django_admin.utils.displays import MoneyDisplay
        
        # Calculate age
        age = timezone.now() - obj.created_at
        age_text = f"{age.days} days, {age.seconds // 3600} hours"
        
        # Build details HTML
        details = []
        
        # Basic info
        details.append(f"<strong>Internal ID:</strong> {obj.internal_payment_id}")
        details.append(f"<strong>Age:</strong> {age_text}")
        
        # Transaction details
        if obj.transaction_hash:
            details.append(f"<strong>Transaction Hash:</strong> {obj.transaction_hash}")
        
        if obj.pay_address:
            details.append(f"<strong>Pay Address:</strong> {obj.pay_address}")
        
        if obj.pay_amount:
            pay_amount_html = MoneyDisplay.amount(
                obj.pay_amount,
                MoneyDisplayConfig(currency="USD")
            )
            details.append(f"<strong>Pay Amount:</strong> {pay_amount_html}")
        
        # URLs
        if obj.callback_url:
            details.append(f"<strong>Callback URL:</strong> {obj.callback_url}")
        
        if obj.cancel_url:
            details.append(f"<strong>Cancel URL:</strong> {obj.cancel_url}")
        
        # Description
        if obj.description:
            details.append(f"<strong>Description:</strong> {obj.description}")
        
        return format_html("<br>".join(details))
    
    payment_details_display.short_description = "Payment Details"
    
    # Actions
    @action(description="Mark as completed", variant=ActionVariant.SUCCESS)
    def mark_completed(self, request, queryset):
        """Mark selected payments as completed."""
        updated = queryset.filter(
            status__in=['pending', 'processing']
        ).update(status='completed')
        
        self.message_user(
            request,
            f"Successfully marked {updated} payment(s) as completed.",
            level='SUCCESS'
        )
    
    @action(description="Mark as failed", variant=ActionVariant.DANGER)
    def mark_failed(self, request, queryset):
        """Mark selected payments as failed."""
        updated = queryset.filter(
            status__in=['pending', 'processing']
        ).update(status='failed')
        
        self.message_user(
                request,
            f"Successfully marked {updated} payment(s) as failed.",
            level='WARNING'
        )
    
    @action(description="Cancel payments", variant=ActionVariant.WARNING)
    def cancel_payments(self, request, queryset):
        """Cancel selected payments."""
        updated = queryset.filter(
            status__in=['pending', 'processing']
        ).update(status='cancelled')
        
        self.message_user(
            request,
            f"Successfully cancelled {updated} payment(s).",
            level='WARNING'
        )
