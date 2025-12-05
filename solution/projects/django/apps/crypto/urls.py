"""
URLs for Crypto app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CoinViewSet, ExchangeViewSet, WalletViewSet

router = DefaultRouter()
router.register(r'coins', CoinViewSet, basename='coin')
router.register(r'exchanges', ExchangeViewSet, basename='exchange')
router.register(r'wallets', WalletViewSet, basename='wallet')

urlpatterns = [
    path('', include(router.urls)),
]
