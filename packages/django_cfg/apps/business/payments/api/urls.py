"""
URL Configuration for Payments v2.0 API.

Nested routes with DRF Router.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CurrencyListView,
    PaymentViewSet,
    BalanceView,
    TransactionListView,
)

app_name = 'payments_api'

# DRF Router for ViewSets
router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    # Currency endpoints
    path('currencies/', CurrencyListView.as_view(), name='currency-list'),

    # Balance endpoints
    path('balance/', BalanceView.as_view(), name='balance'),
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),

    # Payment endpoints (via router)
    # GET    /payments/                    - List payments
    # GET    /payments/{id}/                - Payment detail
    # POST   /payments/create/              - Create payment
    # GET    /payments/{id}/status/         - Check status
    # POST   /payments/{id}/confirm/        - Confirm payment
    path('', include(router.urls)),
]
