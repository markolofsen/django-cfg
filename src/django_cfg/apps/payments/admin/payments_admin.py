"""
Admin interface for payments.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.contrib.humanize.templatetags.humanize import naturaltime
from unfold.admin import ModelAdmin
from unfold.decorators import display

from ..models import UniversalPayment
from .filters import PaymentStatusFilter, PaymentAmountFilter, UserEmailFilter, RecentActivityFilter
from django_cfg.modules.django_logger import get_logger

logger = get_logger("payments_admin")


@admin.register(UniversalPayment)
class UniversalPaymentAdmin(ModelAdmin):
    """Admin interface for universal payments."""
    
    list_display = [
        'payment_display',
        'user_display',
        'amount_display',
        'status_display',
        'provider_display',
        'created_at_display'
    ]
    
    list_display_links = ['payment_display']
    
    search_fields = [
        'internal_payment_id',
        'provider_payment_id',
        'user__email',
        'user__first_name',
        'user__last_name'
    ]
    
    def get_queryset(self, request):
        """Optimize queryset to prevent N+1 queries."""
        return super().get_queryset(request).optimized()
    
    list_filter = [
        PaymentStatusFilter,
        PaymentAmountFilter,
        UserEmailFilter,
        RecentActivityFilter,
        'provider',
        'currency_code',
        'created_at'
    ]
    
    readonly_fields = [
        'internal_payment_id',
        'provider_payment_id',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = [
        ('Payment Information', {
            'fields': ['user', 'amount_usd', 'currency_code', 'description']
        }),
        ('Payment Details', {
            'fields': ['internal_payment_id', 'provider_payment_id', 'provider', 'status']
        }),
        ('Crypto Details', {
            'fields': ['pay_address', 'pay_amount', 'network', 'security_nonce', 'transaction_hash', 'sender_address', 'receiver_address', 'crypto_amount', 'confirmations_count'],
            'classes': ['collapse']
        }),
        ('Provider Data', {
            'fields': ['metadata', 'webhook_data'],
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at', 'expires_at', 'completed_at', 'processed_at'],
            'classes': ['collapse']
        })
    ]
    
    @display(description="Payment")
    def payment_display(self, obj):
        """Display payment ID and description."""
        return format_html(
            '<strong>#{}</strong><br><small>{}</small>',
            obj.internal_payment_id[:8],
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
        """Display amount with currency."""
        return format_html(
            '<span style="font-weight: bold; font-size: 14px;">${}</span><br><small>{}</small>',
            f"{float(obj.amount_usd):.2f}",
            obj.currency_code
        )
    
    @display(description="Status")
    def status_display(self, obj):
        """Display status with color coding."""
        status_colors = {
            'pending': '#ffc107',
            'confirming': '#17a2b8',
            'confirmed': '#28a745',
            'completed': '#28a745',
            'failed': '#dc3545',
            'expired': '#6c757d',
            'cancelled': '#6c757d',
            'refunded': '#fd7e14',
        }
        
        color = status_colors.get(obj.status, '#6c757d')
        
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    
    @display(description="Provider")
    def provider_display(self, obj):
        """Display provider with external ID."""
        provider_colors = {
            'nowpayments': '#007bff',
            'stripe': '#6f42c1',
            'internal': '#28a745',
        }
        
        color = provider_colors.get(obj.provider, '#6c757d')
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span><br><small>{}</small>',
            color,
            obj.get_provider_display(),
            obj.provider_payment_id[:16] + '...' if obj.provider_payment_id and len(obj.provider_payment_id) > 16 else obj.provider_payment_id or '—'
        )
    
    @display(description="Created")
    def created_at_display(self, obj):
        """Display creation date."""
        return naturaltime(obj.created_at)
