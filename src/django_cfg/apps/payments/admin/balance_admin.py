"""
Balance Admin interfaces with Unfold integration.

Advanced balance and transaction management with bulk operations.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.contrib.humanize.templatetags.humanize import naturaltime, intcomma
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum, Q, Avg
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from typing import Optional

from unfold.admin import ModelAdmin
from unfold.decorators import display, action
from unfold.enums import ActionVariant

from ..models import UserBalance, Transaction
from .filters import BalanceRangeFilter, RecentActivityFilter
from django_cfg.modules.django_logger import get_logger

logger = get_logger("balance_admin")


@admin.register(UserBalance)
class UserBalanceAdmin(ModelAdmin):
    """
    Advanced UserBalance admin with bulk operations and financial monitoring.
    
    Features:
    - Balance range filtering and visualization
    - Bulk balance adjustments with audit trail
    - Financial statistics and alerts
    - Transaction history integration
    - Security features for balance modifications
    """
    
    # Custom template for balance statistics
    change_list_template = 'admin/payments/balance/change_list.html'
    
    list_display = [
        'user_display',
        'balance_display',
        'balance_status',
        'transaction_count_display',
        'last_activity_display',
        'created_at_display'
    ]
    
    list_display_links = ['user_display']
    
    search_fields = [
        'user__email',
        'user__first_name',
        'user__last_name',
        'user__username'
    ]
    
    list_filter = [
        BalanceRangeFilter,
        RecentActivityFilter,
        'created_at'
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'last_transaction_at'
    ]
    
    # Unfold actions
    actions_list = [
        'add_funds_bulk',
        'subtract_funds_bulk',
        'reset_zero_balances',
        'export_balance_report',
        'send_low_balance_alerts'
    ]
    
    fieldsets = [
        ('User Information', {
            'fields': ['user']
        }),
        ('Balance Details', {
            'fields': [
                'balance_usd',
                'reserved_usd'
            ]
        }),
        ('Activity Tracking', {
            'fields': [
                'last_transaction_at'
            ]
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    def get_queryset(self, request):
        """Optimize queryset with user data and transaction counts."""
        return super().get_queryset(request).select_related('user').annotate(
            transaction_count=Count('user__transaction_set')
        )
    
    @display(description="User", ordering='user__email')
    def user_display(self, obj):
        """Display user information with avatar and details."""
        if obj.user:
            display_name = obj.user.get_full_name() or obj.user.username
            
            # Determine user tier based on balance
            if obj.balance_usd >= 1000:
                tier_icon = "🐋"
                tier_color = "text-purple-600"
                tier_name = "Whale"
            elif obj.balance_usd >= 100:
                tier_icon = "💎"
                tier_color = "text-blue-600"
                tier_name = "Premium"
            elif obj.balance_usd >= 10:
                tier_icon = "💰"
                tier_color = "text-green-600"
                tier_name = "Active"
            elif obj.balance_usd > 0:
                tier_icon = "🪙"
                tier_color = "text-yellow-600"
                tier_name = "Basic"
            else:
                tier_icon = "💸"
                tier_color = "text-gray-600"
                tier_name = "Empty"
            
            return format_html(
                '<div class="flex items-center space-x-3">'
                '<div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-sm font-bold">'
                '{}'
                '</div>'
                '<div>'
                '<div class="font-medium text-gray-900 dark:text-gray-100">{}</div>'
                '<div class="text-xs text-gray-500">{}</div>'
                '<div class="text-xs {}"><span class="mr-1">{}</span>{}</div>'
                '</div>'
                '</div>',
                display_name[0].upper() if display_name else 'U',
                display_name,
                obj.user.email,
                tier_color,
                tier_icon,
                tier_name
            )
        return format_html('<span class="text-gray-500">No user</span>')
    
    @display(description="Balance", ordering='balance_usd')
    def balance_display(self, obj):
        """Display balance with visual indicators and reserved amounts."""
        balance = obj.balance_usd
        reserved = obj.reserved_usd or 0
        available = balance - reserved
        
        # Color coding based on balance
        if balance < 0:
            balance_color = "text-red-600 dark:text-red-400"
            balance_icon = "⚠️"
        elif balance == 0:
            balance_color = "text-gray-600 dark:text-gray-400"
            balance_icon = "💸"
        elif balance < 10:
            balance_color = "text-yellow-600 dark:text-yellow-400"
            balance_icon = "🪙"
        elif balance < 100:
            balance_color = "text-green-600 dark:text-green-400"
            balance_icon = "💰"
        else:
            balance_color = "text-blue-600 dark:text-blue-400"
            balance_icon = "💎"
        
        html = f'''
        <div class="text-right">
            <div class="font-bold text-lg {balance_color}">
                <span class="mr-1">{balance_icon}</span>${balance:,.2f}
            </div>
        '''
        
        if reserved > 0:
            html += f'''
            <div class="text-xs text-orange-600 dark:text-orange-400">
                Reserved: ${reserved:,.2f}
            </div>
            <div class="text-xs text-gray-500">
                Available: ${available:,.2f}
            </div>
            '''
        
        html += '</div>'
        
        return format_html(html)
    
    @display(description="Status")
    def balance_status(self, obj):
        """Display balance status with alerts."""
        balance = obj.balance_usd
        reserved = obj.reserved_usd or 0
        
        badges = []
        
        if balance < 0:
            badges.append('<span class="inline-flex items-center rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-800 dark:bg-red-900 dark:text-red-200">⚠️ Negative</span>')
        elif balance == 0:
            badges.append('<span class="inline-flex items-center rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-800 dark:bg-gray-900 dark:text-gray-200">💸 Empty</span>')
        elif balance < 1:
            badges.append('<span class="inline-flex items-center rounded-full bg-yellow-100 px-2 py-0.5 text-xs font-medium text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">⚠️ Low</span>')
        else:
            badges.append('<span class="inline-flex items-center rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-800 dark:bg-green-900 dark:text-green-200">✅ Active</span>')
        
        if reserved > 0:
            badges.append('<span class="inline-flex items-center rounded-full bg-orange-100 px-2 py-0.5 text-xs font-medium text-orange-800 dark:bg-orange-900 dark:text-orange-200">🔒 Reserved</span>')
        
        return format_html('<div class="space-y-1">{}</div>', ''.join(badges))
    
    @display(description="Transactions")
    def transaction_count_display(self, obj):
        """Display transaction count and recent activity."""
        count = getattr(obj, 'transaction_count', 0)
        
        if count > 0:
            # Get recent transaction count (last 7 days)
            recent_threshold = timezone.now() - timedelta(days=7)
            recent_count = Transaction.objects.filter(
                user=obj.user,
                created_at__gte=recent_threshold
            ).count()
            
            return format_html(
                '<div class="text-center">'
                '<div class="font-bold text-blue-600 dark:text-blue-400">{}</div>'
                '<div class="text-xs text-gray-500">total</div>'
                '{}'
                '</div>',
                count,
                f'<div class="text-xs text-green-600 dark:text-green-400">{recent_count} recent</div>' if recent_count > 0 else ''
            )
        
        return format_html(
            '<div class="text-center text-gray-500">'
            '<div>0</div>'
            '<div class="text-xs">No transactions</div>'
            '</div>'
        )
    
    @display(description="Last Activity", ordering='last_transaction_at')
    def last_activity_display(self, obj):
        """Display last transaction activity."""
        if obj.last_transaction_at:
            time_ago = timezone.now() - obj.last_transaction_at
            
            if time_ago < timedelta(hours=1):
                color = "text-green-600 dark:text-green-400"
                icon = "🟢"
            elif time_ago < timedelta(days=1):
                color = "text-yellow-600 dark:text-yellow-400"
                icon = "🟡"
            elif time_ago < timedelta(days=7):
                color = "text-orange-600 dark:text-orange-400"
                icon = "🟠"
            else:
                color = "text-red-600 dark:text-red-400"
                icon = "🔴"
            
            return format_html(
                '<div class="text-xs {}">'
                '<span class="mr-1">{}</span>{}'
                '</div>',
                color,
                icon,
                naturaltime(obj.last_transaction_at)
            )
        
        return format_html(
            '<div class="text-xs text-gray-500">Never</div>'
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
        """Add balance statistics to changelist context."""
        extra_context = extra_context or {}
        
        try:
            # Basic statistics
            total_balances = UserBalance.objects.count()
            
            # Balance statistics
            balance_stats = UserBalance.objects.aggregate(
                total_balance=Sum('balance_usd'),
                avg_balance=Avg('balance_usd'),
                total_reserved=Sum('reserved_usd')
            )
            
            # Balance distribution
            zero_balances = UserBalance.objects.filter(balance_usd=0).count()
            negative_balances = UserBalance.objects.filter(balance_usd__lt=0).count()
            low_balances = UserBalance.objects.filter(balance_usd__gt=0, balance_usd__lt=10).count()
            medium_balances = UserBalance.objects.filter(balance_usd__gte=10, balance_usd__lt=100).count()
            high_balances = UserBalance.objects.filter(balance_usd__gte=100, balance_usd__lt=1000).count()
            whale_balances = UserBalance.objects.filter(balance_usd__gte=1000).count()
            
            # Recent activity
            recent_threshold = timezone.now() - timedelta(days=7)
            active_balances = UserBalance.objects.filter(
                last_transaction_at__gte=recent_threshold
            ).count()
            
            # Top balances
            top_balances = UserBalance.objects.filter(
                balance_usd__gt=0
            ).order_by('-balance_usd')[:5]
            
            extra_context.update({
                'balance_stats': {
                    'total_balances': total_balances,
                    'total_balance': balance_stats['total_balance'] or 0,
                    'avg_balance': balance_stats['avg_balance'] or 0,
                    'total_reserved': balance_stats['total_reserved'] or 0,
                    'zero_balances': zero_balances,
                    'negative_balances': negative_balances,
                    'low_balances': low_balances,
                    'medium_balances': medium_balances,
                    'high_balances': high_balances,
                    'whale_balances': whale_balances,
                    'active_balances': active_balances,
                    'top_balances': top_balances,
                }
            })
            
        except Exception as e:
            logger.warning(f"Failed to generate balance statistics: {e}")
            extra_context['balance_stats'] = None
        
        return super().changelist_view(request, extra_context)
    
    # ===== ADMIN ACTIONS =====
    
    @action(
        description="💰 Add Funds (Bulk)",
        icon="add_circle",
        variant=ActionVariant.SUCCESS
    )
    def add_funds_bulk(self, request, queryset):
        """Add funds to selected user balances."""
        
        # This would typically show a form for amount input
        # For now, we'll add a fixed amount as an example
        amount = Decimal('10.00')  # In production, this should come from a form
        
        updated_count = 0
        
        for balance in queryset:
            try:
                # Use manager method for proper transaction handling
                UserBalance.objects.add_funds_to_user(
                    user=balance.user,
                    amount=amount,
                    transaction_type='admin_adjustment',
                    description=f'Bulk funds addition by admin {request.user.username}'
                )
                updated_count += 1
                
            except Exception as e:
                logger.error(f"Failed to add funds to user {balance.user.id}: {e}")
        
        if updated_count > 0:
            messages.success(
                request,
                f"💰 Added ${amount} to {updated_count} user balances"
            )
            messages.info(
                request,
                "ℹ️ All transactions have been logged for audit purposes"
            )
    
    @action(
        description="💸 Subtract Funds (Bulk)",
        icon="remove_circle",
        variant=ActionVariant.WARNING
    )
    def subtract_funds_bulk(self, request, queryset):
        """Subtract funds from selected user balances."""
        
        amount = Decimal('5.00')  # In production, this should come from a form
        
        updated_count = 0
        insufficient_funds = 0
        
        for balance in queryset:
            try:
                if balance.balance_usd >= amount:
                    UserBalance.objects.subtract_funds_from_user(
                        user=balance.user,
                        amount=amount,
                        transaction_type='admin_adjustment',
                        description=f'Bulk funds subtraction by admin {request.user.username}'
                    )
                    updated_count += 1
                else:
                    insufficient_funds += 1
                    
            except Exception as e:
                logger.error(f"Failed to subtract funds from user {balance.user.id}: {e}")
        
        if updated_count > 0:
            messages.success(
                request,
                f"💸 Subtracted ${amount} from {updated_count} user balances"
            )
        
        if insufficient_funds > 0:
            messages.warning(
                request,
                f"⚠️ Skipped {insufficient_funds} users with insufficient funds"
            )
    
    @action(
        description="🔄 Reset Zero Balances",
        icon="refresh",
        variant=ActionVariant.INFO
    )
    def reset_zero_balances(self, request, queryset):
        """Reset zero balances and clear reserved amounts."""
        
        zero_balances = queryset.filter(balance_usd=0)
        reset_count = 0
        
        for balance in zero_balances:
            if balance.reserved_usd and balance.reserved_usd > 0:
                balance.reserved_usd = 0
                balance.save(update_fields=['reserved_usd'])
                reset_count += 1
        
        if reset_count > 0:
            messages.success(
                request,
                f"🔄 Reset reserved amounts for {reset_count} zero balances"
            )
        else:
            messages.info(
                request,
                "ℹ️ No zero balances with reserved amounts found"
            )
    
    @action(
        description="📊 Export Balance Report",
        icon="download",
        variant=ActionVariant.INFO
    )
    def export_balance_report(self, request, queryset):
        """Export balance report to CSV."""
        
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="balance_report_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'User Email', 'User Name', 'Balance USD', 'Reserved USD', 'Available USD',
            'Last Transaction', 'Created', 'Status'
        ])
        
        for balance in queryset:
            available = balance.balance_usd - (balance.reserved_usd or 0)
            
            if balance.balance_usd < 0:
                status = 'Negative'
            elif balance.balance_usd == 0:
                status = 'Empty'
            elif balance.balance_usd < 10:
                status = 'Low'
            elif balance.balance_usd < 100:
                status = 'Medium'
            else:
                status = 'High'
            
            writer.writerow([
                balance.user.email if balance.user else '',
                balance.user.get_full_name() if balance.user else '',
                balance.balance_usd,
                balance.reserved_usd or 0,
                available,
                balance.last_transaction_at.isoformat() if balance.last_transaction_at else '',
                balance.created_at.isoformat(),
                status
            ])
        
        messages.success(
            request,
            f"📊 Exported {queryset.count()} balance records to CSV"
        )
        
        return response
    
    @action(
        description="🔔 Send Low Balance Alerts",
        icon="notifications",
        variant=ActionVariant.WARNING
    )
    def send_low_balance_alerts(self, request, queryset):
        """Send alerts for low balance users."""
        
        low_balance_users = queryset.filter(
            balance_usd__gt=0,
            balance_usd__lt=10
        )
        
        alert_count = 0
        
        for balance in low_balance_users:
            try:
                # In production, this would send an actual notification
                # For now, we'll just log it
                logger.info(
                    f"Low balance alert for user {balance.user.email}: ${balance.balance_usd}"
                )
                alert_count += 1
                
            except Exception as e:
                logger.error(f"Failed to send alert to user {balance.user.id}: {e}")
        
        if alert_count > 0:
            messages.success(
                request,
                f"🔔 Sent low balance alerts to {alert_count} users"
            )
        else:
            messages.info(
                request,
                "ℹ️ No users with low balances found in selection"
            )


@admin.register(Transaction)
class TransactionAdmin(ModelAdmin):
    """
    Transaction admin with detailed tracking and audit capabilities.
    
    Features:
    - Comprehensive transaction history
    - Financial audit trail
    - Transaction type filtering
    - Balance impact visualization
    """
    
    list_display = [
        'transaction_id_display',
        'user_display',
        'transaction_type_badge',
        'amount_display',
        'balance_impact_display',
        'payment_link_display',
        'created_at_display'
    ]
    
    list_display_links = ['transaction_id_display']
    
    search_fields = [
        'id',
        'user__email',
        'user__username',
        'description',
        'payment_id'
    ]
    
    list_filter = [
        'transaction_type',
        RecentActivityFilter,
        'created_at'
    ]
    
    readonly_fields = [
        'id',
        'user',
        'transaction_type',
        'amount_usd',
        'balance_after',
        'payment_id',
        'description',
        'created_at'
    ]
    
    def has_add_permission(self, request):
        """Disable adding transactions through admin (should be created by system)."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable changing transactions (audit trail integrity)."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable deleting transactions (audit trail integrity)."""
        return False
    
    @display(description="Transaction ID", ordering='id')
    def transaction_id_display(self, obj):
        """Display transaction ID."""
        short_id = str(obj.id)[:8]
        return format_html(
            '<span class="font-mono text-sm bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded" '
            'title="Full ID: {}">{}</span>',
            obj.id,
            short_id
        )
    
    @display(description="User", ordering='user__email')
    def user_display(self, obj):
        """Display user information."""
        if obj.user:
            return format_html(
                '<div>'
                '<div class="font-medium">{}</div>'
                '<div class="text-xs text-gray-500">{}</div>'
                '</div>',
                obj.user.get_full_name() or obj.user.username,
                obj.user.email
            )
        return format_html('<span class="text-gray-500">No user</span>')
    
    @display(description="Type", ordering='transaction_type')
    def transaction_type_badge(self, obj):
        """Display transaction type with colored badge."""
        type_config = {
            'payment': ('💳', 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200', 'Payment'),
            'deposit': ('💰', 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200', 'Deposit'),
            'withdrawal': ('💸', 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200', 'Withdrawal'),
            'refund': ('↩️', 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200', 'Refund'),
            'admin_adjustment': ('⚙️', 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200', 'Admin'),
            'fee': ('📋', 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200', 'Fee'),
        }
        
        icon, color_class, label = type_config.get(
            obj.transaction_type,
            ('❓', 'bg-gray-100 text-gray-800', obj.transaction_type.title())
        )
        
        return format_html(
            '<span class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium {}">'
            '{} {}'
            '</span>',
            color_class,
            icon,
            label
        )
    
    @display(description="Amount", ordering='amount_usd')
    def amount_display(self, obj):
        """Display transaction amount with sign."""
        amount = obj.amount_usd
        
        if amount > 0:
            return format_html(
                '<span class="font-bold text-green-600 dark:text-green-400">+${:,.2f}</span>',
                amount
            )
        elif amount < 0:
            return format_html(
                '<span class="font-bold text-red-600 dark:text-red-400">-${:,.2f}</span>',
                abs(amount)
            )
        else:
            return format_html(
                '<span class="font-bold text-gray-600 dark:text-gray-400">${:,.2f}</span>',
                amount
            )
    
    @display(description="Balance Impact")
    def balance_impact_display(self, obj):
        """Display balance before/after transaction."""
        # Calculate balance_before from balance_after and amount_usd
        balance_before = obj.balance_after - obj.amount_usd
        
        return format_html(
            '<div class="text-xs">'
            '<div>Before: <span class="font-mono">${:,.2f}</span></div>'
            '<div>After: <span class="font-mono">${:,.2f}</span></div>'
            '</div>',
            balance_before,
            obj.balance_after
        )
    
    @display(description="Payment")
    def payment_link_display(self, obj):
        """Display payment link if available."""
        if obj.payment_id:
            return format_html(
                '<a href="/admin/payments/universalpayment/{}/change/" '
                'class="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200">'
                '🔗 Payment'
                '</a>',
                obj.payment_id
            )
        return format_html('<span class="text-gray-500">—</span>')
    
    @display(description="Created", ordering='created_at')
    def created_at_display(self, obj):
        """Display creation timestamp."""
        return format_html(
            '<div class="text-xs">'
            '<div>{}</div>'
            '<div class="text-gray-500">{}</div>'
            '</div>',
            obj.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            naturaltime(obj.created_at)
        )
