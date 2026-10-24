"""URL configuration for Crypto app."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.crypto.api import CoinListingViewSet

router = DefaultRouter()
router.register(r"coins", CoinListingViewSet, basename="Coins")

urlpatterns = [
    path("", include(router.urls)),
]
