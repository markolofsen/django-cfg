"""
Payment management views.

Provides list, create, and management functionality for payments.
"""

import json
from django.views.generic import TemplateView, ListView
from .base import (
    SuperuserRequiredMixin,
    PaymentFilterMixin,
    PaymentContextMixin,
    log_view_access
)
from ...models import UniversalPayment, Currency, PaymentProvider
from ...services.providers.registry import ProviderRegistry


class PaymentCreateView(
    SuperuserRequiredMixin,
    PaymentContextMixin,
    TemplateView
):
    """Form view for creating a new payment."""
    
    template_name = 'payments/payment_create.html'
    page_title = 'Create Payment'
    
    def get_breadcrumbs(self):
        return [
            {'name': 'Dashboard', 'url': '/payments/admin/'},
            {'name': 'Payments', 'url': '/payments/admin/list/'},
            {'name': 'Create Payment', 'url': ''},
        ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Log access for audit
        log_view_access('payment_create', self.request.user)
        
        # Get available providers
        providers = self._get_available_providers()
        
        # Get available currencies
        currencies = self._get_available_currencies()
        
        # Get common context
        common_context = self.get_common_context()
        
        # Provider enum with defaults (serialize to JSON for JavaScript)
        provider_defaults = {
            PaymentProvider.NOWPAYMENTS.value: 'USDTTRC20',
            PaymentProvider.CRYPTAPI.value: 'BTC', 
            PaymentProvider.CRYPTOMUS.value: 'USDTTRC20',
            PaymentProvider.STRIPE.value: 'USD'
        }
        provider_defaults_json = json.dumps(provider_defaults)
        
        context.update({
            'providers': providers,
            'currencies': currencies,
            'provider_enum': PaymentProvider,
            'provider_defaults_json': provider_defaults_json,
            'default_amount': 10.0,  # Default test amount
            **common_context
        })
        
        return context
    
    def _get_available_providers(self):
        """Get list of available payment providers from registry."""
        registry = ProviderRegistry()
        provider_names = registry.list_providers()
        
        providers = []
        for provider_name in provider_names:
            provider_instance = registry.get_provider(provider_name)
            providers.append({
                'name': provider_name,
                'display_name': provider_name.title(),
                'is_crypto': provider_name in ['nowpayments', 'cryptapi', 'cryptomus'],
                'description': getattr(provider_instance.__class__, '__doc__', '') if provider_instance else '',
            })
        return providers
    
    def _get_available_currencies(self):
        """Get list of available currencies from database."""
        # Get all active currencies - both fiat and crypto
        return Currency.objects.all().order_by('currency_type', 'code')
    
    


class PaymentListView(
    SuperuserRequiredMixin,
    PaymentFilterMixin,
    PaymentContextMixin,
    ListView
):
    """Paginated list view for all payments."""
    
    model = UniversalPayment
    template_name = 'payments/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 20
    ordering = ['-created_at']
    page_title = 'All Payments'
    
    def get_breadcrumbs(self):
        return [
            {'name': 'Dashboard', 'url': '/payments/admin/'},
            {'name': 'All Payments', 'url': ''},
        ]
    
    def get_queryset(self):
        # Log access for audit
        log_view_access('payment_list', self.request.user)
        
        # Use filter mixin to get filtered queryset
        return self.get_filtered_payments().order_by(*self.ordering)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filter context
        filter_context = self.get_filter_context()
        
        # Get available filter options
        filter_options = self._get_filter_options()
        
        # Get common context
        common_context = self.get_common_context()
        
        context.update({
            'filters': filter_context,
            'filter_options': filter_options,
            'total_count': self.get_queryset().count(),
            **common_context
        })
        
        return context
    
    def _get_filter_options(self):
        """Get available options for filter dropdowns."""

        # Get unique statuses
        statuses = UniversalPayment.objects.values_list('status', flat=True).distinct()
        status_choices = [(status, status.title()) for status in statuses if status]
        
        # Get unique providers
        providers = UniversalPayment.objects.values_list('provider', flat=True).distinct()
        provider_choices = [(provider, provider.title()) for provider in providers if provider]
        
        return {
            'statuses': status_choices,
            'providers': provider_choices,
        }
