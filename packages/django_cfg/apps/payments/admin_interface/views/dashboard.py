"""
Admin Dashboard Template Views.

Django template views for admin dashboard interface.
"""

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator

from .base import AdminTemplateViewMixin


@method_decorator(staff_member_required, name='dispatch')
class PaymentDashboardView(AdminTemplateViewMixin, LoginRequiredMixin, TemplateView):
    """
    Main admin dashboard view.
    
    Displays overview of payments, webhooks, and system statistics.
    """
    
    template_name = 'payments/payment_dashboard.html'
    
    def get_context_data(self, **kwargs):
        """Add dashboard context data."""
        context = super().get_context_data(**kwargs)
        
        context.update({
            'page_title': 'Payment Dashboard',
            'page_subtitle': 'Overview of payment system activity',
            'show_stats': True,
            'auto_refresh': True,
        })
        
        return context


@method_decorator(staff_member_required, name='dispatch')
class WebhookDashboardView(AdminTemplateViewMixin, LoginRequiredMixin, TemplateView):
    """
    Webhook dashboard view.
    
    Displays webhook events, provider status, and ngrok configuration.
    """
    
    template_name = 'payments/webhook_dashboard.html'
    
    def get_context_data(self, **kwargs):
        """Add webhook dashboard context data."""
        context = super().get_context_data(**kwargs)
        
        context.update({
            'page_title': 'Webhook Dashboard',
            'page_subtitle': 'Monitor and test webhook endpoints',
            'show_ngrok_status': True,
            'auto_refresh': True,
        })
        
        return context
