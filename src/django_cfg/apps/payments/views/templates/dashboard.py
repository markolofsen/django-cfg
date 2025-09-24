"""
Main payment dashboard view.

Provides overview, statistics, and recent payments for superuser access.
"""

from django.views.generic import TemplateView
from .base import (
    SuperuserRequiredMixin, 
    PaymentFilterMixin, 
    PaymentStatsMixin, 
    PaymentContextMixin,
    log_view_access
)


class PaymentDashboardView(
    SuperuserRequiredMixin,
    PaymentFilterMixin,
    PaymentStatsMixin,
    PaymentContextMixin,
    TemplateView
):
    """Main payment dashboard with overview and recent payments."""
    
    template_name = 'payments/dashboard.html'
    page_title = 'Payment Dashboard'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Log access for audit
        log_view_access('dashboard', self.request.user)
        
        # Get filtered payments
        payments_qs = self.get_filtered_payments()
        
        # Get recent payments (limit to 20 for performance)
        recent_payments = payments_qs.order_by('-created_at')[:20]
        
        # Check if there are more payments for pagination
        has_more = payments_qs.count() > 20
        
        # Get statistics
        payment_stats = self.get_payment_stats()
        provider_stats = self.get_provider_stats()
        
        # Get common context
        common_context = self.get_common_context()
        
        context.update({
            'payments': recent_payments,
            'has_more_payments': has_more,
            'payment_stats': payment_stats,
            'provider_stats': provider_stats,
            'filters': self.get_filter_context(),
            **common_context
        })
        
        return context
