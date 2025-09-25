"""
Payment system ViewSets router for easy integration.
"""

from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import (
    # Balance ViewSets
    UserBalanceViewSet, TransactionViewSet,
    
    # Payment ViewSets
    UserPaymentViewSet, UniversalPaymentViewSet,
    
    # Subscription ViewSets
    UserSubscriptionViewSet, SubscriptionViewSet, EndpointGroupViewSet,
    
    # API Key ViewSets
    UserAPIKeyViewSet, APIKeyViewSet,
    
    # Currency ViewSets
    CurrencyViewSet, NetworkViewSet, ProviderCurrencyViewSet,
    
    # Tariff ViewSets
    TariffViewSet, TariffEndpointGroupViewSet,
)


class PaymentSystemRouter:
    """Universal router with all payment endpoints"""
    
    def __init__(self):
        self.router = DefaultRouter()
        self._setup_main_routes()
        
    def _setup_main_routes(self):
        """Setup main resource routes"""
        # Core payment resources
        self.router.register(r'payments', UniversalPaymentViewSet, basename='payment')
        self.router.register(r'balances', UserBalanceViewSet, basename='balance')
        self.router.register(r'transactions', TransactionViewSet, basename='transaction')
        
        # Subscription management
        self.router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
        self.router.register(r'endpoint-groups', EndpointGroupViewSet, basename='endpoint-group')
        
        # API key management
        self.router.register(r'api-keys', APIKeyViewSet, basename='api-key')
        
        # Currency and pricing
        self.router.register(r'currencies', CurrencyViewSet, basename='currency')
        self.router.register(r'networks', NetworkViewSet, basename='network')
        self.router.register(r'provider-currencies', ProviderCurrencyViewSet, basename='provider-currency')
        self.router.register(r'tariffs', TariffViewSet, basename='tariff')
        self.router.register(r'tariff-groups', TariffEndpointGroupViewSet, basename='tariff-group')
    
    @property
    def urls(self):
        """Get all URLs"""
        return self.router.urls


# Create default router instance
payment_router = PaymentSystemRouter()

__all__ = ['PaymentSystemRouter', 'payment_router']
