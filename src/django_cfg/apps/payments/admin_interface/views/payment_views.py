"""
Payment Template Views for Universal Payment System v2.0.

Django template views for payment forms and status pages.
"""

from django.views.generic import TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils import timezone

from ...models import UniversalPayment
from ...services.core.payment_service import PaymentService
from ...services.core.currency_service import CurrencyService
from ...services.integrations.providers_config import get_all_providers_info


class PaymentFormView(LoginRequiredMixin, TemplateView):
    """
    Payment creation form view.
    
    Displays a form for creating new payments with provider selection
    and real-time currency conversion.
    """
    template_name = 'payments/payment_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add form data
        context.update({
            'page_title': 'Create Payment',
            'page_subtitle': 'Process a payment through our universal payment system',
        })
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle AJAX payment creation."""
        if not request.headers.get('Content-Type', '').startswith('application/json'):
            return super().get(request, *args, **kwargs)
        
        try:
            import json
            data = json.loads(request.body)
            
            # Create payment using service
            payment_service = PaymentService()
            result = payment_service.create_payment(
                user_id=request.user.id,
                amount_usd=float(data.get('amount', 0)),
                currency_code=data.get('currency', 'USD'),
                provider=data.get('provider'),
                callback_url=data.get('callback_url')
            )
            
            if result.success:
                return JsonResponse({
                    'success': True,
                    'payment': {
                        'id': str(result.data.id),
                        'external_id': result.data.external_id,
                        'status': result.data.status,
                        'amount_usd': result.data.amount_usd,
                        'currency_code': result.data.currency_code,
                        'provider': result.data.provider,
                        'payment_url': result.data.payment_url,
                        'qr_code_url': result.data.qr_code_url,
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result.error_message
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class PaymentStatusView(DetailView):
    """
    Payment status tracking view.
    
    Displays payment status with real-time updates and timeline.
    """
    model = UniversalPayment
    template_name = 'payments/payment_status.html'
    context_object_name = 'payment'
    
    def get_object(self, queryset=None):
        """Get payment by ID with optimized query."""
        if queryset is None:
            queryset = self.get_queryset()
        
        # Get payment ID from URL
        payment_id = self.kwargs.get('pk')
        
        return get_object_or_404(
            queryset.select_related('currency', 'user')
                   .prefetch_related('transactions'),
            id=payment_id
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payment = self.object
        
        # Add page metadata
        context.update({
            'page_title': f'Payment #{payment.external_id or str(payment.id)[:8]}',
            'page_subtitle': 'Track your payment progress in real-time',
        })
        
        return context
    
    def get(self, request, *args, **kwargs):
        """Handle both template and AJAX requests."""
        self.object = self.get_object()
        
        # Handle AJAX requests for status updates
        if request.headers.get('Accept') == 'application/json':
            payment = self.object
            
            return JsonResponse({
                'id': str(payment.id),
                'external_id': payment.external_id,
                'status': payment.status,
                'status_display': payment.get_status_display(),
                'amount_usd': payment.amount_usd,
                'amount_crypto': str(payment.amount_crypto) if payment.amount_crypto else None,
                'currency_code': payment.currency.code,
                'provider': payment.provider,
                'network': payment.network,
                'created_at': payment.created_at.isoformat(),
                'updated_at': payment.updated_at.isoformat(),
                'confirmed_at': payment.confirmed_at.isoformat() if payment.confirmed_at else None,
                'payment_url': payment.payment_url,
                'qr_code_url': payment.qr_code_url,
                'exchange_rate': str(payment.exchange_rate) if payment.exchange_rate else None,
            })
        
        # Regular template response
        return super().get(request, *args, **kwargs)


class PaymentListView(LoginRequiredMixin, TemplateView):
    """
    Payment list view with filtering and search.
    
    Displays a paginated list of payments with advanced filtering options.
    """
    template_name = 'payments/payment_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add page metadata
        context.update({
            'page_title': 'Payment History',
            'page_subtitle': 'View and manage your payment transactions',
        })
        
        return context


class PaymentDashboardView(LoginRequiredMixin, TemplateView):
    """
    Main payment dashboard view.
    
    Displays payment statistics, recent activity, and quick actions.
    """
    template_name = 'payments/payment_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get payment statistics
        user_payments = UniversalPayment.objects.filter(user=self.request.user)
        
        stats = {
            'total_payments': user_payments.count(),
            'completed_payments': user_payments.filter(status='completed').count(),
            'pending_payments': user_payments.filter(status__in=['pending', 'processing']).count(),
            'failed_payments': user_payments.filter(status__in=['failed', 'cancelled']).count(),
            'total_amount': sum(p.amount_usd for p in user_payments.filter(status='completed')),
            'recent_payments': user_payments.order_by('-created_at')[:5],
        }
        
        # Add page metadata
        context.update({
            'page_title': 'Payment Dashboard',
            'page_subtitle': 'Overview of your payment activity',
            'stats': stats,
        })
        
        return context


class CurrencyConverterView(TemplateView):
    """
    Currency conversion tool view.
    
    Provides real-time currency conversion rates and calculator.
    """
    template_name = 'payments/currency_converter.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add page metadata
        context.update({
            'page_title': 'Currency Converter',
            'page_subtitle': 'Real-time currency conversion rates',
        })
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle AJAX conversion requests."""
        if not request.headers.get('Content-Type', '').startswith('application/json'):
            return super().get(request, *args, **kwargs)
        
        try:
            import json
            data = json.loads(request.body)
            
            # Use currency service for conversion
            currency_service = CurrencyService()
            result = currency_service.convert_currency(
                amount=float(data.get('amount', 0)),
                from_currency=data.get('from_currency', 'USD'),
                to_currency=data.get('to_currency', 'BTC')
            )
            
            if result.success:
                return JsonResponse({
                    'success': True,
                    'converted_amount': result.data.converted_amount,
                    'exchange_rate': result.data.exchange_rate,
                    'from_currency': result.data.from_currency,
                    'to_currency': result.data.to_currency,
                    'timestamp': timezone.now().isoformat(),
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result.error_message
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
