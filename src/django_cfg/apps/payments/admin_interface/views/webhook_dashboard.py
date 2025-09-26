"""
Webhook dashboard template view.

Simple dashboard for monitoring webhook activity and provider status.
"""

from django.views.generic import TemplateView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse


@method_decorator(staff_member_required, name='dispatch')
class WebhookDashboardView(TemplateView):
    """
    Webhook dashboard for monitoring and management.
    
    Provides a simple interface for:
    - Viewing webhook provider configurations
    - Monitoring webhook activity
    - Testing webhook endpoints
    - Checking ngrok status
    """
    
    template_name = 'payments/webhook_dashboard.html'
    
    def get_context_data(self, **kwargs):
        """Add dashboard context data."""
        context = super().get_context_data(**kwargs)
        
        # Basic context - the real data comes from API endpoints
        context.update({
            'page_title': 'Webhook Dashboard',
            'auto_refresh': True,  # Enable auto-refresh
        })
        
        return context
