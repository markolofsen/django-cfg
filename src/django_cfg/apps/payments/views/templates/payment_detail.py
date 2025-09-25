"""
Payment detail view.

Provides detailed information about a single payment for superuser access.
"""

from django.views.generic import DetailView
from .base import (
    SuperuserRequiredMixin,
    PaymentContextMixin,
    log_view_access
)
from ...models import UniversalPayment, PaymentEvent


class PaymentDetailView(
    SuperuserRequiredMixin,
    PaymentContextMixin,
    DetailView
):
    """Detailed view for a single payment."""
    
    model = UniversalPayment
    template_name = 'payments/payment_detail.html'
    context_object_name = 'payment'
    page_title = 'Payment Details'
    
    def get_breadcrumbs(self):
        payment = self.get_object()
        return [
            {'name': 'Dashboard', 'url': '/payments/admin/'},
            {'name': 'Payments', 'url': '/payments/admin/list/'},
            {'name': f'Payment #{payment.internal_payment_id or str(payment.id)[:8]}', 'url': ''},
        ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payment = self.get_object()
        
        # Log access for audit
        log_view_access('payment_detail', self.request.user, payment_id=payment.id)
        
        # Get payment events for this payment
        events = PaymentEvent.objects.filter(payment_id=payment.id).order_by('-created_at')
        
        # Get related payments (same user, similar amount range)
        related_payments = UniversalPayment.objects.filter(
            user=payment.user,
            amount_usd__gte=payment.amount_usd * 0.8,
            amount_usd__lte=payment.amount_usd * 1.2
        ).exclude(id=payment.id).order_by('-created_at')[:5]
        
        # Get provider-specific information
        provider_info = self._get_provider_info(payment)
        
        # Get common context
        common_context = self.get_common_context()
        
        context.update({
            'events': events,
            'related_payments': related_payments,
            'provider_info': provider_info,
            'can_retry': self._can_retry_payment(payment),
            'can_cancel': self._can_cancel_payment(payment),
            'can_refund': self._can_refund_payment(payment),
            **common_context
        })
        
        return context
    
    def _get_provider_info(self, payment):
        """Get provider-specific information for the payment."""
        info = {
            'display_name': payment.provider.title(),
            'is_crypto': payment.provider in ['nowpayments', 'cryptapi', 'cryptomus'],
            'supports_qr': payment.provider in ['nowpayments', 'cryptapi', 'cryptomus'],
            'supports_webhook': True,
        }
        
        # Add crypto-specific info
        if info['is_crypto'] and payment.pay_address:
            info.update({
                'crypto_address': payment.pay_address,
                'crypto_amount': payment.pay_amount,
                'crypto_currency': payment.currency_code,
                'network': getattr(payment, 'network', 'mainnet'),
                'confirmations': getattr(payment, 'confirmations_count', 0),
            })
        
        return info
    
    def _can_retry_payment(self, payment):
        """Check if payment can be retried."""
        return payment.status in ['failed', 'expired']
    
    def _can_cancel_payment(self, payment):
        """Check if payment can be cancelled."""
        return payment.status in ['pending', 'confirming']
    
    def _can_refund_payment(self, payment):
        """Check if payment can be refunded."""
        return payment.status == 'completed'
