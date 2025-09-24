"""
QR code views for crypto payments.

Provides QR code generation and display for cryptocurrency payments.
"""

from django.views.generic import DetailView
from django.http import JsonResponse
from .base import (
    SuperuserRequiredMixin,
    PaymentContextMixin,
    superuser_required,
    log_view_access
)
from ...models import UniversalPayment


class PaymentQRCodeView(
    SuperuserRequiredMixin,
    PaymentContextMixin,
    DetailView
):
    """QR code view for crypto payments."""
    
    model = UniversalPayment
    template_name = 'payments/payment_qr.html'
    context_object_name = 'payment'
    page_title = 'Payment QR Code'
    
    def get_breadcrumbs(self):
        payment = self.get_object()
        return [
            {'name': 'Dashboard', 'url': '/payments/admin/'},
            {'name': 'Payments', 'url': '/payments/admin/list/'},
            {'name': f'Payment #{payment.internal_payment_id or str(payment.id)[:8]}', 
             'url': f'/payments/admin/payment/{payment.id}/'},
            {'name': 'QR Code', 'url': ''},
        ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payment = self.get_object()
        
        # Log access for audit
        log_view_access('payment_qr', self.request.user, payment_id=payment.id)
        
        # Check if payment supports QR codes
        if not self._supports_qr_code(payment):
            context['error'] = "QR codes are not supported for this payment method"
            return context
        
        # Generate QR code data
        qr_data = self._generate_qr_data(payment)
        
        # Get payment instructions
        instructions = self._get_payment_instructions(payment)
        
        # Get common context
        common_context = self.get_common_context()
        
        context.update({
            'qr_data': qr_data,
            'qr_size': self.request.GET.get('size', 256),
            'instructions': instructions,
            'is_crypto': self._is_crypto_payment(payment),
            'can_copy': True,
            **common_context
        })
        
        return context
    
    def _supports_qr_code(self, payment):
        """Check if payment method supports QR codes."""
        crypto_providers = ['nowpayments', 'cryptapi', 'cryptomus']
        return payment.provider in crypto_providers and payment.pay_address
    
    def _is_crypto_payment(self, payment):
        """Check if payment is cryptocurrency-based."""
        crypto_providers = ['nowpayments', 'cryptapi', 'cryptomus']
        return payment.provider in crypto_providers
    
    def _generate_qr_data(self, payment):
        """Generate QR code data for the payment."""
        if not payment.pay_address:
            return None
        
        # For crypto payments, use standard format
        if self._is_crypto_payment(payment):
            qr_data = payment.pay_address
            
            # Add amount if available
            if payment.pay_amount:
                # Use appropriate URI scheme based on currency
                uri_schemes = {
                    'BTC': 'bitcoin',
                    'LTC': 'litecoin',
                    'ETH': 'ethereum',
                    'BCH': 'bitcoincash',
                }
                
                scheme = uri_schemes.get(payment.currency_code.upper(), 'crypto')
                qr_data = f"{scheme}:{payment.pay_address}?amount={payment.pay_amount}"
                
                # Add label if available
                if payment.internal_payment_id:
                    qr_data += f"&label=Payment%20{payment.internal_payment_id}"
            
            return qr_data
        
        return payment.pay_address
    
    def _get_payment_instructions(self, payment):
        """Get step-by-step payment instructions."""
        if not self._is_crypto_payment(payment):
            return []
        
        instructions = [
            "Scan the QR code with your crypto wallet app",
            f"Send exactly {payment.pay_amount} {payment.currency_code} to the address",
            "Wait for network confirmations",
            "Payment will be automatically confirmed"
        ]
        
        # Add provider-specific instructions
        if payment.provider == 'cryptapi':
            instructions.append("Minimum 1 confirmation required")
        elif payment.provider == 'nowpayments':
            instructions.append("Minimum 2 confirmations required")
        elif payment.provider == 'cryptomus':
            instructions.append("Confirmations depend on selected network")
        
        return instructions


@superuser_required
def qr_code_data_ajax(request, payment_id):
    """AJAX endpoint to get QR code data."""
    try:
        payment = UniversalPayment.objects.get(id=payment_id)
        
        # Log access for audit
        log_view_access('qr_ajax', request.user, payment_id=payment_id)
        
        view = PaymentQRCodeView()
        
        # Check if payment supports QR codes
        if not view._supports_qr_code(payment):
            return JsonResponse({
                'error': 'QR codes not supported for this payment method'
            }, status=400)
        
        # Generate QR data
        qr_data = view._generate_qr_data(payment)
        
        if not qr_data:
            return JsonResponse({
                'error': 'Unable to generate QR code data'
            }, status=400)
        
        response_data = {
            'qr_data': qr_data,
            'payment_address': payment.pay_address,
            'payment_amount': str(payment.pay_amount) if payment.pay_amount else None,
            'currency': payment.currency_code,
            'provider': payment.provider,
            'instructions': view._get_payment_instructions(payment),
        }
        
        return JsonResponse(response_data)
        
    except UniversalPayment.DoesNotExist:
        return JsonResponse({'error': 'Payment not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
