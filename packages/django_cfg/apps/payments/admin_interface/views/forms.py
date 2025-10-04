"""
Admin Form Template Views.

Django template views for payment forms and detail pages.
"""

from django.views.generic import TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404

from .base import AdminTemplateViewMixin
from django_cfg.apps.payments.models import UniversalPayment


@method_decorator(staff_member_required, name='dispatch')
class PaymentFormView(AdminTemplateViewMixin, LoginRequiredMixin, TemplateView):
    """
    Payment creation form view.
    
    Displays form for creating new payments with provider selection.
    """
    
    template_name = 'payments/payment_form.html'
    
    def get_context_data(self, **kwargs):
        """Add form context data."""
        context = super().get_context_data(**kwargs)
        
        context.update({
            'page_title': 'Create Payment',
            'page_subtitle': 'Process a payment through the universal payment system',
            'form_mode': 'create',
        })
        
        return context


@method_decorator(staff_member_required, name='dispatch')
class PaymentDetailView(AdminTemplateViewMixin, LoginRequiredMixin, DetailView):
    """
    Payment detail view.
    
    Displays detailed information about a specific payment.
    """
    
    model = UniversalPayment
    template_name = 'payments/payment_detail.html'
    context_object_name = 'payment'
    
    def get_queryset(self):
        """Optimized queryset with related objects."""
        return UniversalPayment.objects.select_related('user', 'currency', 'network')
    
    def get_context_data(self, **kwargs):
        """Add detail context data."""
        context = super().get_context_data(**kwargs)
        
        payment = self.get_object()
        
        # Force refresh from database to get latest data
        payment.refresh_from_db()
        
        context.update({
            'payment': payment,
            'page_title': f'Payment {payment.internal_payment_id or payment.id}',
            'page_subtitle': f'Payment details and transaction history',
            'show_actions': True,
            'can_cancel': payment.status in ['pending', 'confirming'],
            'can_refund': payment.status == 'completed',
        })
        
        return context


@method_decorator(staff_member_required, name='dispatch')
class PaymentListView(AdminTemplateViewMixin, LoginRequiredMixin, TemplateView):
    """
    Payment list view.
    
    Displays paginated list of payments with filtering options.
    """
    
    template_name = 'payments/payment_list.html'
    
    def get_context_data(self, **kwargs):
        """Add list context data."""
        context = super().get_context_data(**kwargs)
        
        context.update({
            'page_title': 'Payment List',
            'page_subtitle': 'Manage and monitor all payments',
            'show_filters': True,
            'show_bulk_actions': True,
        })
        
        return context
