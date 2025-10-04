"""
Balance Admin interfaces using Django Admin Utilities.

Clean, modern admin interfaces with no HTML duplication.
"""

from django.contrib import admin
from django.db.models import Count, Sum, Q, Avg
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

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
from django_cfg.modules.django_logging import get_logger

from ..models import UserBalance, Transaction
from .filters import BalanceRangeFilter, RecentActivityFilter

logger = get_logger("balance_admin")


@admin.register(UserBalance)
class UserBalanceAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin):
    """
    UserBalance admin using Django Admin Utilities.
    
    Features:
    - Clean display utilities with no HTML duplication
    - Automatic query optimization
    - Type-safe configuration
    - Unfold integration
    """
    
    # Performance optimization
    select_related_fields = ['user']
    annotations = {
        'transaction_count': Count('user__payment_transactions')
    }
    
    # List configuration
    list_display = [
        'user_display',
        'balance_display',
        'status_display',
        'transaction_count_display',
        'updated_display'
    ]
    
    list_filter = [
        BalanceRangeFilter,
        RecentActivityFilter,
        'created_at',
        'updated_at',
    ]
    
    search_fields = [
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name'
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'balance_breakdown_display'
    ]
    
    # Register actions
    actions = ['reset_zero_balances']
    
    # Display methods using Unfold features
    @display(description="User", header=True)
    def user_display(self, obj):
        """User display with avatar using Unfold header feature."""
        if not obj.user:
            return ["No user", "", ""]
        
        return [
            obj.user.get_full_name() or obj.user.username,
            obj.user.email,
            obj.user.get_full_name()[:2].upper() if obj.user.get_full_name() else obj.user.username[:2].upper()
        ]
    
    @display(description="Balance", ordering="balance_usd")
    def balance_display(self, obj):
        """Balance display using utilities."""
        return self.display_money_amount(
            obj, 
            'balance_usd',
            MoneyDisplayConfig(currency="USD", show_sign=False)
        )
    
    @display(description="Status", label={
        "Empty": "danger",
        "Low Balance": "warning", 
        "Active": "success",
        "High Balance": "info"
    })
    def status_display(self, obj):
        """Status display using Unfold label feature."""
        if obj.balance_usd <= 0:
            return "Empty"
        elif obj.balance_usd < 10:
            return "Low Balance"
        elif obj.balance_usd < 100:
            return "Active"
        else:
            return "High Balance"
    
    @display(description="Transactions")
    def transaction_count_display(self, obj):
        """Transaction count using utilities."""
        count = getattr(obj, 'transaction_count', 0)
        return self.display_count_simple(
            obj, 
            'transaction_count', 
            'transactions'
        )
    
    @display(description="Updated")
    def updated_display(self, obj):
        """Updated time using utilities."""
        return self.display_datetime_relative(
            obj, 
            'updated_at',
            DateTimeDisplayConfig(show_relative=True, show_seconds=False)
        )
    
    # Readonly field displays
    def balance_breakdown_display(self, obj):
        """Detailed balance breakdown for detail view."""
        if not obj.pk:
            return "Save to see breakdown"
        
        breakdown_items = []
        
        # Main balance
        if hasattr(obj, 'reserved_usd') and obj.reserved_usd:
            available = obj.balance_usd - obj.reserved_usd
            breakdown_items = [
                {'label': 'Reserved', 'amount': obj.reserved_usd, 'color': 'warning'},
                {'label': 'Available', 'amount': available, 'color': 'success'}
            ]
        
        from django_cfg.modules.django_admin.utils.displays import MoneyDisplay
        return MoneyDisplay.with_breakdown(
            obj.balance_usd,
            breakdown_items,
            MoneyDisplayConfig(currency="USD")
        )
    
    balance_breakdown_display.short_description = "Balance Breakdown"
    
    # Actions using utilities
    @action(description="Reset zero balances", variant=ActionVariant.WARNING)
    def reset_zero_balances(self, request, queryset):
        """Reset balances that are zero."""
        updated = queryset.filter(balance_usd=0).update(reserved_usd=0)
        self.message_user(
            request,
            f"Successfully reset {updated} zero balance(s).",
            level='WARNING'
        )


@admin.register(Transaction)
class TransactionAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin):
    """
    Transaction admin using Django Admin Utilities.
    
    Clean interface for transaction management.
    """
    
    # Performance optimization
    select_related_fields = ['user']
    
    # List configuration
    list_display = [
        'transaction_id_display',
        'user_display',
        'amount_display',
        'type_display',
        'status_display',
        'created_display'
    ]
    
    list_filter = [
        'transaction_type',
        RecentActivityFilter,
        'created_at'
    ]
    
    search_fields = [
        'id',
        'user__username',
        'user__email',
        'description'
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at'
    ]
    
    # Display methods
    @display(description="ID")
    def transaction_id_display(self, obj):
        """Transaction ID display."""
        return StatusBadge.create(
            text=str(obj.id)[:8] + "...",
            variant="info"
        )
    
    @display(description="User")
    def user_display(self, obj):
        """User display."""
        return self.display_user_simple(obj, 'user')
    
    @display(description="Amount")
    def amount_display(self, obj):
        """Amount display with sign."""
        return self.display_money_amount(
            obj,
            'amount_usd',
            MoneyDisplayConfig(currency="USD", show_sign=True)
        )
    
    @display(description="Type", label=True)
    def type_display(self, obj):
        """Transaction type display."""
        return self.display_status_auto(
            type('obj', (), {'status': obj.transaction_type})(),
            'status'
        )
    
    @display(description="Status", label=True)
    def status_display(self, obj):
        """Status display."""
        # Transaction model doesn't have status field, show type instead
        return self.display_status_auto(
            type('obj', (), {'status': obj.transaction_type})(),
            'status'
        )
    
    @display(description="Created")
    def created_display(self, obj):
        """Created time display."""
        return self.display_datetime_compact(obj, 'created_at')
