"""
Utility views for payment dashboard.

Provides testing, debugging, and development functionality.
"""

from django.views.generic import TemplateView
from django.utils import timezone
from datetime import timedelta
from .base import (
    SuperuserRequiredMixin,
    PaymentContextMixin,
    log_view_access
)


class PaymentTestView(
    SuperuserRequiredMixin,
    PaymentContextMixin,
    TemplateView
):
    """Test view for development and debugging purposes."""
    
    template_name = 'payments/test.html'
    page_title = 'Payment System Test'
    
    def get_breadcrumbs(self):
        return [
            {'name': 'Dashboard', 'url': '/payments/admin/'},
            {'name': 'System Test', 'url': ''},
        ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Log access for audit
        log_view_access('payment_test', self.request.user)
        
        # Create sample data for testing templates
        sample_data = self._generate_sample_data()
        
        # Get system information
        system_info = self._get_system_info()
        
        # Get test scenarios
        test_scenarios = self._get_test_scenarios()
        
        # Get common context
        common_context = self.get_common_context()
        
        context.update({
            'sample_data': sample_data,
            'system_info': system_info,
            'test_scenarios': test_scenarios,
            'test_mode': True,
            **common_context
        })
        
        return context
    
    def _generate_sample_data(self):
        """Generate sample payment data for testing."""
        sample_payments = []
        statuses = ['pending', 'confirming', 'completed', 'failed']
        providers = ['nowpayments', 'cryptapi', 'cryptomus', 'stripe']
        
        for i in range(12):
            sample_payments.append({
                'id': f'sample-{i}',
                'internal_payment_id': f'PAY-{1000 + i}',
                'provider_payment_id': f'PROV-{2000 + i}',
                'amount_usd': 50.0 + (i * 25),
                'currency_code': 'USD',
                'status': statuses[i % len(statuses)],
                'provider': providers[i % len(providers)],
                'user_email': f'user{i}@example.com',
                'created_at': timezone.now() - timedelta(hours=i),
                'updated_at': timezone.now() - timedelta(minutes=i * 10),
                'pay_address': f'1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa{i}' if i % 2 == 0 else None,
                'pay_amount': 0.001 + (i * 0.0001) if i % 2 == 0 else None,
            })
        
        return {
            'payments': sample_payments,
            'stats': {
                'total_count': len(sample_payments),
                'pending_count': len([p for p in sample_payments if p['status'] == 'pending']),
                'completed_count': len([p for p in sample_payments if p['status'] == 'completed']),
                'failed_count': len([p for p in sample_payments if p['status'] == 'failed']),
                'total_volume': sum(p['amount_usd'] for p in sample_payments),
            }
        }
    
    def _get_system_info(self):
        """Get system information for debugging."""
        import django
        import sys
        from django.conf import settings
        
        info = {
            'django_version': django.get_version(),
            'python_version': sys.version,
            'debug_mode': settings.DEBUG,
            'database_engine': settings.DATABASES['default']['ENGINE'],
            'installed_apps': len(settings.INSTALLED_APPS),
            'timezone': str(settings.TIME_ZONE),
            'language': settings.LANGUAGE_CODE,
        }
        
        # Add payment-specific info
        try:
            from ...models import UniversalPayment, PaymentEvent
            info.update({
                'total_payments': UniversalPayment.objects.count(),
                'total_events': PaymentEvent.objects.count(),
                'providers_in_use': list(
                    UniversalPayment.objects.values_list('provider', flat=True).distinct()
                ),
            })
        except Exception:
            info.update({
                'total_payments': 'Unable to query',
                'total_events': 'Unable to query',
                'providers_in_use': [],
            })
        
        return info
    
    def _get_test_scenarios(self):
        """Get available test scenarios."""
        scenarios = [
            {
                'name': 'Template Component Test',
                'description': 'Test all payment template components with sample data',
                'endpoint': '/payments/test/?test=components',
                'available': True,
            },
            {
                'name': 'Status Badge Test',
                'description': 'Test payment status badges for all possible statuses',
                'endpoint': '/payments/test/?test=status_badges',
                'available': True,
            },
            {
                'name': 'Progress Bar Test',
                'description': 'Test payment progress bars with different percentages',
                'endpoint': '/payments/test/?test=progress_bars',
                'available': True,
            },
            {
                'name': 'Provider Statistics Test',
                'description': 'Test provider statistics with sample data',
                'endpoint': '/payments/test/?test=provider_stats',
                'available': True,
            },
            {
                'name': 'Real-time Updates Test',
                'description': 'Test WebSocket connections and real-time updates',
                'endpoint': '/payments/test/?test=realtime',
                'available': False,  # Requires WebSocket setup
            },
            {
                'name': 'QR Code Generation Test',
                'description': 'Test QR code generation for crypto payments',
                'endpoint': '/payments/test/?test=qr_codes',
                'available': True,
            },
            {
                'name': 'API Integration Test',
                'description': 'Test payment provider API integrations',
                'endpoint': '/payments/test/?test=api_integration',
                'available': False,  # Requires API keys
            },
        ]
        
        # Add current test parameter
        current_test = self.request.GET.get('test', 'overview')
        for scenario in scenarios:
            scenario['is_current'] = scenario['endpoint'].endswith(f'test={current_test}')
        
        return scenarios
