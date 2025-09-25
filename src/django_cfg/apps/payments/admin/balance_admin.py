"""
Admin interfaces for balance and transaction management.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.urls import reverse
from django.shortcuts import redirect
from unfold.admin import ModelAdmin
from unfold.decorators import display, action
from unfold.enums import ActionVariant

from ..models import UserBalance, Transaction
from .filters import BalanceRangeFilter, TransactionTypeFilter, UserEmailFilter, RecentActivityFilter


@admin.register(UserBalance)
class UserBalanceAdmin(ModelAdmin):
    """Admin interface for user balances."""
    
    list_display = [
        'user_display',
        'balance_display',
        'reserved_display',
        'available_display',
        'last_transaction_display',
        'created_at_display'
    ]
    
    list_display_links = ['user_display']
    
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    
    list_filter = [
        BalanceRangeFilter,
        UserEmailFilter,
        RecentActivityFilter,
        'created_at'
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'transaction_history',
        'balance_statistics'
    ]
    
    fieldsets = [
        ('User Information', {
            'fields': ['user']
        }),
        ('Balance Details', {
            'fields': ['amount_usd', 'reserved_usd']
        }),
        ('Statistics', {
            'fields': ['balance_statistics'],
            'classes': ['collapse']
        }),
        ('Transaction History', {
            'fields': ['transaction_history'],
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    actions_detail = ['add_funds', 'view_transactions']
    
    @display(description="User")
    def user_display(self, obj):
        """Display user with avatar."""
        user = obj.user
        if hasattr(user, 'avatar') and user.avatar:
            avatar_html = f'<img src="{user.avatar.url}" style="width: 24px; height: 24px; border-radius: 50%; margin-right: 8px;" />'
        else:
            initials = f"{user.first_name[:1]}{user.last_name[:1]}" if user.first_name and user.last_name else user.email[:2]
            avatar_html = f'<div style="width: 24px; height: 24px; border-radius: 50%; background: #6c757d; color: white; display: inline-flex; align-items: center; justify-content: center; font-size: 10px; margin-right: 8px;">{initials.upper()}</div>'
        
        return format_html(
            '{}<strong>{}</strong><br><small>{}</small>',
            avatar_html,
            user.get_full_name() or user.email,
            user.email
        )
    
    @display(description="Balance")
    def balance_display(self, obj):
        """Display balance with color coding."""
        amount = obj.amount_usd
        if amount > 100:
            color = '#28a745'  # Green
        elif amount > 10:
            color = '#ffc107'  # Yellow
        elif amount > 0:
            color = '#fd7e14'  # Orange
        else:
            color = '#dc3545'  # Red
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">${}</span>',
            color, f"{float(amount):.2f}"
        )
    
    @display(description="Reserved")
    def reserved_display(self, obj):
        """Display reserved amount."""
        if obj.reserved_usd > 0:
            return format_html(
                '<span style="color: #6c757d;">${}</span>',
                f"{float(obj.reserved_usd):.2f}"
            )
        return "—"
    
    @display(description="Available")
    def available_display(self, obj):
        """Display available balance."""
        available = obj.amount_usd - obj.reserved_usd
        return format_html(
            '<span style="font-weight: bold;">${}</span>',
            f"{float(available):.2f}"
        )
    
    @display(description="Last Transaction")
    def last_transaction_display(self, obj):
        """Display last transaction."""
        last_transaction = obj.user.transactions.order_by('-created_at').first()
        if last_transaction:
            return format_html(
                '<span style="color: {};">{} ${}</span><br><small>{}</small>',
                '#28a745' if last_transaction.amount_usd > 0 else '#dc3545',
                '+' if last_transaction.amount_usd > 0 else '',
                f"{float(abs(last_transaction.amount_usd)):.2f}",
                naturaltime(last_transaction.created_at)
            )
        return "No transactions"
    
    @display(description="Created")
    def created_at_display(self, obj):
        """Display creation date."""
        return naturaltime(obj.created_at)
    
    def balance_statistics(self, obj):
        """Show balance statistics."""
        transactions = obj.user.transactions.all()
        total_credited = sum(t.amount_usd for t in transactions if t.amount_usd > 0)
        total_debited = sum(abs(t.amount_usd) for t in transactions if t.amount_usd < 0)
        transaction_count = transactions.count()
        
        return format_html(
            '<div style="line-height: 1.6;">'
            '<strong>Statistics:</strong><br>'
            '• Total Credited: <span style="color: #28a745;">${}</span><br>'
            '• Total Debited: <span style="color: #dc3545;">${}</span><br>'
            '• Net Balance: <span style="color: {};">${}</span><br>'
            '• Total Transactions: {}<br>'
            '• Available Balance: <strong>${}</strong>'
            '</div>',
            f"{float(total_credited):.2f}",
            f"{float(total_debited):.2f}",
            '#28a745' if (total_credited - total_debited) > 0 else '#dc3545',
            f"{float(total_credited - total_debited):.2f}",
            transaction_count,
            f"{float(obj.amount_usd - obj.reserved_usd):.2f}"
        )
    
    balance_statistics.short_description = "Balance Statistics"
    
    def transaction_history(self, obj):
        """Show recent transaction history."""
        transactions = obj.user.transactions.order_by('-created_at')[:10]
        
        if not transactions:
            return "No transactions"
        
        html = '<div style="line-height: 1.8;">'
        for transaction in transactions:
            amount_color = '#28a745' if transaction.amount_usd > 0 else '#dc3545'
            amount_sign = '+' if transaction.amount_usd > 0 else ''
            
            html += f'''
            <div style="border-bottom: 1px solid #eee; padding: 4px 0;">
                <span style="color: {amount_color}; font-weight: bold;">
                    {amount_sign}${abs(transaction.amount_usd):.2f}
                </span>
                <span style="margin-left: 10px; color: #6c757d;">
                    {transaction.get_transaction_type_display()}
                </span>
                <br>
                <small style="color: #999;">
                    {transaction.description[:50]}{'...' if len(transaction.description) > 50 else ''}
                    • {naturaltime(transaction.created_at)}
                </small>
            </div>
            '''
        
        if obj.user.transactions.count() > 10:
            html += f'<p><small><em>... and {obj.user.transactions.count() - 10} more transactions</em></small></p>'
        
        html += '</div>'
        return format_html(html)
    
    transaction_history.short_description = "Recent Transactions"
    
    @action(
        description="💰 Add Funds",
        icon="attach_money",
        variant=ActionVariant.SUCCESS
    )
    def add_funds(self, request, object_id):
        """Add funds to user balance."""
        # In real implementation, this would redirect to a custom form
        balance = self.get_object(request, object_id)
        if balance:
            self.message_user(
                request,
                f"Add funds form would open for {balance.user.email}",
                level='info'
            )
        return redirect(request.META.get('HTTP_REFERER', '/admin/'))
    
    @action(
        description="📊 View Transactions",
        icon="receipt_long",
        variant=ActionVariant.INFO
    )
    def view_transactions(self, request, object_id):
        """View all transactions for this user."""
        balance = self.get_object(request, object_id)
        if balance:
            url = reverse('admin:django_cfg_payments_transaction_changelist')
            return redirect(f"{url}?user__id__exact={balance.user.id}")
        return redirect(request.META.get('HTTP_REFERER', '/admin/'))


@admin.register(Transaction)
class TransactionAdmin(ModelAdmin):
    """Admin interface for transactions."""
    
    list_display = [
        'transaction_display',
        'user_display',
        'amount_display',
        'type_display',
        'payment_display',
        'subscription_display',
        'created_at_display'
    ]
    
    list_display_links = ['transaction_display']
    
    search_fields = [
        'user__email',
        'description',
        'payment__internal_payment_id',
        'subscription__endpoint_group__name'
    ]
    
    list_filter = [
        TransactionTypeFilter,
        UserEmailFilter,
        RecentActivityFilter,
        'payment__status',
        'subscription__status',
        'created_at'
    ]
    
    readonly_fields = [
        'created_at',
        'transaction_details',
        'related_objects'
    ]
    
    fieldsets = [
        ('Transaction Information', {
            'fields': ['user', 'transaction_type', 'amount_usd', 'description']
        }),
        ('Related Objects', {
            'fields': ['payment', 'subscription'],
            'classes': ['collapse']
        }),
        ('Additional Data', {
            'fields': ['metadata', 'related_objects'],
            'classes': ['collapse']
        }),
        ('Transaction Details', {
            'fields': ['transaction_details'],
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ['created_at'],
            'classes': ['collapse']
        })
    ]
    
    @display(description="Transaction")
    def transaction_display(self, obj):
        """Display transaction ID and description."""
        return format_html(
            '<strong>#{}</strong><br><small>{}</small>',
            str(obj.id)[:8],
            obj.description[:40] + '...' if len(obj.description) > 40 else obj.description
        )
    
    @display(description="User")
    def user_display(self, obj):
        """Display user information."""
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            obj.user.get_full_name() or obj.user.email,
            obj.user.email
        )
    
    @display(description="Amount")
    def amount_display(self, obj):
        """Display amount with color coding."""
        amount = obj.amount_usd
        color = '#28a745' if amount > 0 else '#dc3545'
        sign = '+' if amount > 0 else ''
        
        return format_html(
            '<span style="color: {}; font-weight: bold; font-size: 14px;">{}</span>',
            color,
            f'{sign}${abs(amount):.2f}'
        )
    
    @display(description="Type")
    def type_display(self, obj):
        """Display transaction type with badge."""
        type_colors = {
            'credit': '#28a745',
            'debit': '#dc3545',
            'refund': '#17a2b8',
            'withdrawal': '#ffc107',
        }
        
        color = type_colors.get(obj.transaction_type, '#6c757d')
        
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_transaction_type_display()
        )
    
    @display(description="Payment")
    def payment_display(self, obj):
        """Display related payment."""
        if obj.payment:
            return format_html(
                '<a href="{}" style="color: #007bff;">#{}</a><br><small>{}</small>',
                reverse('admin:django_cfg_payments_universalpayment_change', args=[obj.payment.id]),
                obj.payment.internal_payment_id[:8],
                obj.payment.get_status_display()
            )
        return "—"
    
    @display(description="Subscription")
    def subscription_display(self, obj):
        """Display related subscription."""
        if obj.subscription:
            return format_html(
                '<a href="{}" style="color: #007bff;">{}</a><br><small>{}</small>',
                reverse('admin:django_cfg_payments_subscription_change', args=[obj.subscription.id]),
                obj.subscription.endpoint_group.display_name,
                obj.subscription.get_tier_display()
            )
        return "—"
    
    @display(description="Created")
    def created_at_display(self, obj):
        """Display creation date."""
        return naturaltime(obj.created_at)
    
    def transaction_details(self, obj):
        """Show detailed transaction information."""
        return format_html(
            '<div style="line-height: 1.6;">'
            '<strong>Transaction Details:</strong><br>'
            '• ID: {}<br>'
            '• User: {} ({})<br>'
            '• Type: {}<br>'
            '• Amount: <span style="color: {};">${}</span><br>'
            '• Description: {}<br>'
            '• Created: {}<br>'
            '{}'
            '{}'
            '</div>',
            obj.id,
            obj.user.get_full_name() or 'No name',
            obj.user.email,
            obj.get_transaction_type_display(),
            '#28a745' if obj.amount_usd > 0 else '#dc3545',
            f"{float(obj.amount_usd):.2f}",
            obj.description,
            obj.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            f'• Payment: {obj.payment.internal_payment_id}<br>' if obj.payment else '',
            f'• Subscription: {obj.subscription.endpoint_group.name}<br>' if obj.subscription else ''
        )
    
    transaction_details.short_description = "Transaction Details"
    
    def related_objects(self, obj):
        """Show related objects."""
        html = '<div style="line-height: 1.6;">'
        
        if obj.payment:
            html += f'''
            <strong>Related Payment:</strong><br>
            • ID: {obj.payment.internal_payment_id}<br>
            • Status: {obj.payment.get_status_display()}<br>
            • Amount: ${obj.payment.amount_usd:.2f}<br>
            • Provider: {obj.payment.provider}<br>
            '''
        
        if obj.subscription:
            html += f'''
            <strong>Related Subscription:</strong><br>
            • Endpoint: {obj.subscription.endpoint_group.display_name}<br>
            • Tier: {obj.subscription.get_tier_display()}<br>
            • Status: {obj.subscription.get_status_display()}<br>
            • Usage: {obj.subscription.usage_current}/{obj.subscription.usage_limit}<br>
            '''
        
        if obj.metadata:
            html += '<strong>Metadata:</strong><br>'
            for key, value in obj.metadata.items():
                html += f'• {key}: {value}<br>'
        
        html += '</div>'
        return format_html(html)
    
    related_objects.short_description = "Related Objects"
