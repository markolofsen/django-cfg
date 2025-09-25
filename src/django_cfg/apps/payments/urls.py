"""
URL routing for universal payments with nested routers.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from . import views

app_name = 'payments'

# Main router for global endpoints
router = DefaultRouter()

# Global ViewSets (without user nesting)
router.register(r'payments', views.UniversalPaymentViewSet, basename='payment')
router.register(r'subscriptions', views.SubscriptionViewSet, basename='subscription')
router.register(r'api-keys', views.APIKeyViewSet, basename='apikey')
router.register(r'balances', views.UserBalanceViewSet, basename='balance')
router.register(r'transactions', views.TransactionViewSet, basename='transaction')
router.register(r'currencies', views.CurrencyViewSet, basename='currency')
router.register(r'networks', views.NetworkViewSet, basename='network')
router.register(r'provider-currencies', views.ProviderCurrencyViewSet, basename='providercurrency')
router.register(r'endpoint-groups', views.EndpointGroupViewSet, basename='endpointgroup')
router.register(r'tariffs', views.TariffViewSet, basename='tariff')
router.register(r'tariff-endpoint-groups', views.TariffEndpointGroupViewSet, basename='tariffendpointgroup')

# Nested routers for user-specific resources
# /users/{user_id}/payments/
users_router = routers.SimpleRouter()
users_router.register(r'users', views.UserPaymentViewSet, basename='user')

payments_router = routers.NestedSimpleRouter(users_router, r'users', lookup='user')
payments_router.register(r'payments', views.UserPaymentViewSet, basename='user-payment')

# /users/{user_id}/subscriptions/
subscriptions_router = routers.NestedSimpleRouter(users_router, r'users', lookup='user')
subscriptions_router.register(r'subscriptions', views.UserSubscriptionViewSet, basename='user-subscription')

# /users/{user_id}/api-keys/
apikeys_router = routers.NestedSimpleRouter(users_router, r'users', lookup='user')
apikeys_router.register(r'api-keys', views.UserAPIKeyViewSet, basename='user-apikey')

# Generic API endpoints
generic_patterns = [
    # Payment endpoints
    path('payment/create/', views.PaymentCreateView.as_view(), name='payment-create'),
    path('payment/status/<str:internal_payment_id>/', views.PaymentStatusView.as_view(), name='payment-status'),
    
    # Subscription endpoints
    path('subscription/create/', views.SubscriptionCreateView.as_view(), name='subscription-create'),
    path('subscriptions/active/', views.ActiveSubscriptionsView.as_view(), name='subscriptions-active'),
    
    # API Key endpoints
    path('api-key/create/', views.APIKeyCreateView.as_view(), name='apikey-create'),
    path('api-key/validate/', views.APIKeyValidateView.as_view(), name='apikey-validate'),
    
    # Currency endpoints
    path('currencies/supported/', views.SupportedCurrenciesView.as_view(), name='currencies-supported'),
    path('currencies/rates/', views.CurrencyRatesView.as_view(), name='currency-rates'),
    
    # Tariff endpoints
    path('tariffs/available/', views.AvailableTariffsView.as_view(), name='tariffs-available'),
    path('tariffs/comparison/', views.TariffComparisonView.as_view(), name='tariff-comparison'),
]

urlpatterns = [
    # Include all router URLs
    path('', include(router.urls)),
    
    # Include nested router URLs
    path('', include(payments_router.urls)),
    path('', include(subscriptions_router.urls)),
    path('', include(apikeys_router.urls)),
    
    # Include generic API endpoints
    path('', include(generic_patterns)),
    
]
