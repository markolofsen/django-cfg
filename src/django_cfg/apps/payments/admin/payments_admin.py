"""
Payment Admin interface with Unfold integration.

Advanced payment management with filtering, actions, and monitoring.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.contrib.humanize.templatetags.humanize import naturaltime, intcomma
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from typing import Optional

from unfold.admin import ModelAdmin
from unfold.decorators import display, action
from unfold.enums import ActionVariant

from ..models import UniversalPayment
from .filters import PaymentStatusFilter, PaymentAmountFilter, UserEmailFilter, RecentActivityFilter
from django_cfg.modules.django_logger import get_logger

logger = get_logger("payments_admin")


@admin.register(UniversalPayment)
class UniversalPaymentAdmin(ModelAdmin):
    """
    Advanced Payment admin with Unfold styling and comprehensive management features.
    
    Features:
    - Real-time status tracking with visual indicators
    - Advanced filtering and search capabilities
    - Bulk operations for payment management
    - Provider-specific information display
    - Financial statistics and monitoring
    """
    
    # Custom template for payment statistics
    change_list_template = 'admin/payments/payment/change_list.html'
    
    list_display = [
        'payment_id_display',
        'user_display',
        'amount_display',
        'status_display',
        'provider_display',
        'currency_display',
        'progress_display',
        'created_at_display'
    ]
    
    list_display_links = ['payment_id_display']
    
    search_fields = [
        'id',
        'provider_payment_id',
        'user__email',
        'user__first_name',
        'user__last_name',
        'user__username',
        'description'
    ]
    
    list_filter = [
        PaymentStatusFilter,
        PaymentAmountFilter,
        UserEmailFilter,
        RecentActivityFilter,
        'provider',
        'currency',
        'created_at'
    ]
    
    readonly_fields = [
        'id',
        'provider_payment_id',
        'payment_url',
        'created_at',
        'updated_at',
        'completed_at'
    ]
    
    # Unfold actions
    actions_list = [
        'check_payment_status',
        'cancel_selected_payments',
        'mark_as_completed',
        'export_payment_data'
    ]
    
    fieldsets = [
        ('Payment Information', {
            'fields': [
                'id',
                'user',
                'amount_usd',
                'currency',
                'crypto_amount',
                'description'
            ]
        }),
        ('Provider Details', {
            'fields': [
                'provider',
                'provider_payment_id',
                'payment_url'
            ]
        }),
        ('Status & Tracking', {
            'fields': [
                'status',
                'error_code',
                'error_message',
                'expires_at'
            ]
        }),
        ('URLs & Callbacks', {
            'fields': [
                'callback_url',
                'cancel_url'
            ],
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': [
                'metadata'
            ],
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': [
                'created_at',
                'updated_at',
                'completed_at'
            ],
            'classes': ['collapse']
        })
    ]
    
    def get_queryset(self, request):
        """Optimize queryset with user data."""
        return super().get_queryset(request).select_related('user')
    
    @display(description="Payment ID", ordering='id')
    def payment_id_display(self, obj):
        """Display payment ID with copy functionality."""
        short_id = str(obj.id)[:8]
        return format_html(
            '<span class="font-mono text-sm bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded" '
            'title="Click to copy full ID: {}">{}</span>',
            obj.id,
            short_id
        )
    
    @display(description="User", ordering='user__email')
    def user_display(self, obj):
        """Display user information with avatar."""
        if obj.user:
            display_name = obj.user.get_full_name() or obj.user.username
            return format_html(
                '<div class="flex items-center space-x-2">'
                '<div class="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-xs font-bold">'
                '{}'
                '</div>'
                '<div>'
                '<div class="font-medium text-gray-900 dark:text-gray-100">{}</div>'
                '<div class="text-xs text-gray-500">{}</div>'
                '</div>'
                '</div>',
                display_name[0].upper() if display_name else 'U',
                display_name,
                obj.user.email
            )
        return format_html('<span class="text-gray-500">No user</span>')
    
    @display(description="Amount", ordering='amount_usd')
    def amount_display(self, obj):
        """Display amount with currency conversion."""
        usd_amount = f"${obj.amount_usd:,.2f}"
        
        if obj.amount_crypto and obj.currency:
            crypto_display = f"{obj.amount_crypto:.8f}".rstrip('0').rstrip('.')
            return format_html(
                '<div class="text-right">'
                '<div class="font-bold text-green-600 dark:text-green-400">{}</div>'
                '<div class="text-xs text-gray-500">{} {}</div>'
                '</div>',
                usd_amount,
                crypto_display,
                obj.currency.code
            )
        
        return format_html(
            '<div class="text-right font-bold text-green-600 dark:text-green-400">{}</div>',
            usd_amount
        )
    
    @display(description="Status", ordering='status')
    def status_display(self, obj):
        """Display status with colored badge and icon."""
        status_config = {
            UniversalPayment.PaymentStatus.PENDING: ('🟡', 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200', 'Pending'),
            UniversalPayment.PaymentStatus.WAITING_FOR_PAYMENT: ('⏰', 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200', 'Waiting'),
            UniversalPayment.PaymentStatus.CONFIRMING: ('🔄', 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200', 'Confirming'),
            UniversalPayment.PaymentStatus.COMPLETED: ('✅', 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200', 'Completed'),
            UniversalPayment.PaymentStatus.FAILED: ('❌', 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200', 'Failed'),
            UniversalPayment.PaymentStatus.CANCELLED: ('🚫', 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200', 'Cancelled'),
            UniversalPayment.PaymentStatus.EXPIRED: ('⌛', 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200', 'Expired'),
            UniversalPayment.PaymentStatus.REFUNDED: ('↩️', 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200', 'Refunded'),
        }
        
        icon, color_class, label = status_config.get(
            obj.status, 
            ('❓', 'bg-gray-100 text-gray-800', 'Unknown')
        )
        
        return format_html(
            '<span class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium {}">'
            '{} {}'
            '</span>',
            color_class,
            icon,
            label
        )
    
    @display(description="Provider", ordering='provider')
    def provider_display(self, obj):
        """Display provider with logo/icon."""
        provider_config = {
            'nowpayments': ('🟦', 'NowPayments'),
            'cryptomus': ('🟩', 'Cryptomus'),
            'cryptapi': ('🟪', 'CryptAPI'),
        }
        
        icon, name = provider_config.get(obj.provider, ('🔷', obj.provider.title()))
        
        return format_html(
            '<span class="inline-flex items-center space-x-1">'
            '<span>{}</span>'
            '<span class="text-sm font-medium">{}</span>'
            '</span>',
            icon,
            name
        )
    
    @display(description="Currency", ordering='currency__code')
    def currency_display(self, obj):
        """Display currency with type indicator."""
        if obj.currency:
            # Use currency type from model
            is_crypto = obj.currency.currency_type == 'crypto'
            
            icon = '₿' if is_crypto else '💰'
            
            return format_html(
                '<span class="inline-flex items-center space-x-1">'
                '<span>{}</span>'
                '<span class="font-mono font-bold">{}</span>'
                '</span>',
                icon,
                obj.currency.code
            )
        
        return format_html('<span class="text-gray-500">—</span>')
    
    @display(description="Progress")
    def progress_display(self, obj):
        """Display payment progress with time information."""
        now = timezone.now()
        
        # Calculate time since creation
        time_elapsed = now - obj.created_at
        
        # Check if expired
        if obj.expires_at and now > obj.expires_at:
            return format_html(
                '<div class="text-red-500 text-xs">'
                '⌛ Expired<br>'
                '<span class="text-gray-400">{}</span>'
                '</div>',
                naturaltime(obj.expires_at)
            )
        
        # Show time remaining if has expiry
        if obj.expires_at:
            time_remaining = obj.expires_at - now
            if time_remaining.total_seconds() > 0:
                return format_html(
                    '<div class="text-orange-500 text-xs">'
                    '⏰ {} left<br>'
                    '<span class="text-gray-400">Created {}</span>'
                    '</div>',
                    naturaltime(now + time_remaining),
                    naturaltime(obj.created_at)
                )
        
        # Default: show creation time
        return format_html(
            '<div class="text-gray-500 text-xs">'
            'Created<br>'
            '<span>{}</span>'
            '</div>',
            naturaltime(obj.created_at)
        )
    
    @display(description="Created", ordering='created_at')
    def created_at_display(self, obj):
        """Display creation date with relative time."""
        return format_html(
            '<div class="text-xs">'
            '<div class="font-medium">{}</div>'
            '<div class="text-gray-500">{}</div>'
            '</div>',
            obj.created_at.strftime('%Y-%m-%d %H:%M'),
            naturaltime(obj.created_at)
        )
    
    def changelist_view(self, request, extra_context=None):
        """Add payment statistics to changelist context."""
        extra_context = extra_context or {}
        
        try:
            # Basic statistics
            total_payments = UniversalPayment.objects.count()
            
            # Status distribution
            status_stats = {}
            for status in UniversalPayment.PaymentStatus:
                count = UniversalPayment.objects.filter(status=status).count()
                status_stats[status] = count
            
            # Financial statistics
            total_amount = UniversalPayment.objects.aggregate(
                total=Sum('amount_usd')
            )['total'] or 0
            
            completed_amount = UniversalPayment.objects.filter(
                status=UniversalPayment.PaymentStatus.COMPLETED
            ).aggregate(total=Sum('amount_usd'))['total'] or 0
            
            # Recent activity (24 hours)
            recent_threshold = timezone.now() - timedelta(hours=24)
            recent_payments = UniversalPayment.objects.filter(
                created_at__gte=recent_threshold
            ).count()
            
            recent_amount = UniversalPayment.objects.filter(
                created_at__gte=recent_threshold
            ).aggregate(total=Sum('amount_usd'))['total'] or 0
            
            # Provider statistics
            provider_stats = UniversalPayment.objects.values('provider').annotate(
                count=Count('id'),
                amount=Sum('amount_usd')
            ).order_by('-count')
            
            # Success rate
            completed_count = status_stats.get(UniversalPayment.PaymentStatus.COMPLETED, 0)
            success_rate = (completed_count / total_payments * 100) if total_payments > 0 else 0
            
            extra_context.update({
                'payment_stats': {
                    'total_payments': total_payments,
                    'status_stats': status_stats,
                    'total_amount': total_amount,
                    'completed_amount': completed_amount,
                    'recent_payments': recent_payments,
                    'recent_amount': recent_amount,
                    'provider_stats': provider_stats,
                    'success_rate': success_rate,
                }
            })
            
        except Exception as e:
            logger.warning(f"Failed to generate payment statistics: {e}")
            extra_context['payment_stats'] = None
        
        return super().changelist_view(request, extra_context)
    
    # ===== ADMIN ACTIONS =====
    
    @action(
        description="🔍 Check Payment Status",
        icon="refresh",
        variant=ActionVariant.INFO
    )
    def check_payment_status(self, request, queryset):
        """Check payment status with providers."""
        
        updated_count = 0
        error_count = 0
        
        for payment in queryset:
            try:
                # Use payment service to check status
                from ..services.core.payment_service import PaymentService
                
                service = PaymentService()
                result = service.check_payment_status(payment.id)
                
                if result.success:
                    updated_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                error_count += 1
                logger.error(f"Failed to check payment status for {payment.id}: {e}")
        
        if updated_count > 0:
            messages.success(
                request,
                f"✅ Checked status for {updated_count} payments"
            )
        
        if error_count > 0:
            messages.warning(
                request,
                f"⚠️ Failed to check {error_count} payments"
            )
    
    @action(
        description="🚫 Cancel Selected Payments",
        icon="cancel",
        variant=ActionVariant.WARNING
    )
    def cancel_selected_payments(self, request, queryset):
        """Cancel selected payments."""
        
        # Only allow cancellation of pending/waiting payments
        cancelable_payments = queryset.filter(
            status__in=[
                UniversalPayment.PaymentStatus.PENDING,
                UniversalPayment.PaymentStatus.WAITING_FOR_PAYMENT
            ]
        )
        
        cancelled_count = 0
        
        for payment in cancelable_payments:
            try:
                payment.mark_cancelled(reason="Cancelled by admin")
                cancelled_count += 1
                
            except Exception as e:
                logger.error(f"Failed to cancel payment {payment.id}: {e}")
        
        if cancelled_count > 0:
            messages.success(
                request,
                f"🚫 Cancelled {cancelled_count} payments"
            )
        
        skipped_count = queryset.count() - cancelled_count
        if skipped_count > 0:
            messages.info(
                request,
                f"ℹ️ Skipped {skipped_count} payments (not cancelable)"
            )
    
    @action(
        description="✅ Mark as Completed",
        icon="check_circle",
        variant=ActionVariant.SUCCESS
    )
    def mark_as_completed(self, request, queryset):
        """Mark selected payments as completed (admin override)."""
        
        # Only allow completion of pending/waiting/confirming payments
        completable_payments = queryset.filter(
            status__in=[
                UniversalPayment.PaymentStatus.PENDING,
                UniversalPayment.PaymentStatus.WAITING_FOR_PAYMENT,
                UniversalPayment.PaymentStatus.CONFIRMING
            ]
        )
        
        completed_count = 0
        
        for payment in completable_payments:
            try:
                payment.mark_completed()
                completed_count += 1
                
            except Exception as e:
                logger.error(f"Failed to complete payment {payment.id}: {e}")
        
        if completed_count > 0:
            messages.success(
                request,
                f"✅ Marked {completed_count} payments as completed"
            )
            messages.warning(
                request,
                "⚠️ Admin override used - ensure payments were actually received!"
            )
        
        skipped_count = queryset.count() - completed_count
        if skipped_count > 0:
            messages.info(
                request,
                f"ℹ️ Skipped {skipped_count} payments (not completable)"
            )
    
    @action(
        description="📊 Export Payment Data",
        icon="download",
        variant=ActionVariant.INFO
    )
    def export_payment_data(self, request, queryset):
        """Export selected payments to CSV."""
        
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="payments_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'User Email', 'Amount USD', 'Currency', 'Crypto Amount',
            'Status', 'Provider', 'Created', 'Completed', 'Description'
        ])
        
        for payment in queryset:
            writer.writerow([
                str(payment.id),
                payment.user.email if payment.user else '',
                payment.amount_usd,
                payment.currency.code if payment.currency else '',
                payment.amount_crypto or '',
                payment.status,
                payment.provider,
                payment.created_at.isoformat(),
                payment.completed_at.isoformat() if payment.completed_at else '',
                payment.description or ''
            ])
        
        messages.success(
            request,
            f"📊 Exported {queryset.count()} payments to CSV"
        )
        
        return response
