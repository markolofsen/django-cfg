"""
URLs for Crypto app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CoinViewSet, ExchangeViewSet, WalletViewSet
from .views.api import ClientCommandViewSet

router = DefaultRouter()
router.register(r'coins', CoinViewSet, basename='coin')
router.register(r'exchanges', ExchangeViewSet, basename='exchange')
router.register(r'wallets', WalletViewSet, basename='wallet')
router.register(r'commands', ClientCommandViewSet, basename='client-command')

urlpatterns = [
    path('', include(router.urls)),
]
