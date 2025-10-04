"""
API URL routing for the Universal Payment System v2.0.

DRF routing with nested routers and custom endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views.api import (
    PaymentViewSet, UserPaymentViewSet, PaymentCreateView, PaymentStatusView,
    UserBalanceViewSet, TransactionViewSet, UserTransactionViewSet,
    CurrencyViewSet, NetworkViewSet, ProviderCurrencyViewSet, CurrencyRatesView, SupportedCurrenciesView,
    SubscriptionViewSet, UserSubscriptionViewSet, EndpointGroupViewSet, TariffViewSet,
    APIKeyViewSet, UserAPIKeyViewSet, APIKeyCreateView, APIKeyValidateView,
    UniversalWebhookView, webhook_health_check, webhook_stats, supported_providers,
)
from .views.overview import urls as overview_urls

app_name = 'cfg_payments'

# Main router for global endpoints
router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'balances', UserBalanceViewSet, basename='balance')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'currencies', CurrencyViewSet, basename='currency')
router.register(r'networks', NetworkViewSet, basename='network')
router.register(r'provider-currencies', ProviderCurrencyViewSet, basename='provider-currency')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'endpoint-groups', EndpointGroupViewSet, basename='endpoint-group')
router.register(r'tariffs', TariffViewSet, basename='tariff')
router.register(r'api-keys', APIKeyViewSet, basename='api-key')

# Nested routers for user-specific resources
users_router = routers.SimpleRouter()
users_router.register(r'users', UserPaymentViewSet, basename='user') # Base for nesting

payments_router = routers.NestedSimpleRouter(users_router, r'users', lookup='user')
payments_router.register(r'payments', UserPaymentViewSet, basename='user-payment')

subscriptions_router = routers.NestedSimpleRouter(users_router, r'users', lookup='user')
subscriptions_router.register(r'subscriptions', UserSubscriptionViewSet, basename='user-subscription')

apikeys_router = routers.NestedSimpleRouter(users_router, r'users', lookup='user')
apikeys_router.register(r'api-keys', UserAPIKeyViewSet, basename='user-api-key')

urlpatterns = [
    # Include all router URLs
    path('', include(router.urls)),
    
    # Include nested router URLs
    path('', include(users_router.urls)),
    path('', include(payments_router.urls)),
    path('', include(subscriptions_router.urls)),
    path('', include(apikeys_router.urls)),
    
    # Custom API endpoints
    path('payments/create/', PaymentCreateView.as_view(), name='payment-create'),
    path('payments/status/<uuid:pk>/', PaymentStatusView.as_view(), name='payment-status'),
    
    # Note: currencies/convert/ is handled by CurrencyViewSet action
    # path('currencies/convert/', CurrencyConversionView.as_view(), name='currency-convert'),
    path('currencies/rates/', CurrencyRatesView.as_view(), name='currency-rates'),
    path('currencies/supported/', SupportedCurrenciesView.as_view(), name='currencies-supported'),
    
    path('api-keys/create/', APIKeyCreateView.as_view(), name='apikey-create'),
    path('api-keys/validate/', APIKeyValidateView.as_view(), name='apikey-validate'),
    
    # Webhook endpoints - specific endpoints MUST come before generic <provider> pattern
    path('webhooks/health/', webhook_health_check, name='webhook-health'),
    path('webhooks/stats/', webhook_stats, name='webhook-stats'),
    path('webhooks/providers/', supported_providers, name='webhook-providers'),
    path('webhooks/<str:provider>/', UniversalWebhookView.as_view(), name='webhook-handler'),
    
    # Health check endpoint
    path('health/', PaymentViewSet.as_view({'get': 'health'}), name='health-check'),
    
    # Overview dashboard endpoints
    path('overview/', include(overview_urls)),
]
