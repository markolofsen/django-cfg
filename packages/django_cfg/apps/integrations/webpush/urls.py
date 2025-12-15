"""
URL patterns for Web Push module.

API endpoints for Web Push notifications.
"""

from django.urls import include, path
from rest_framework import routers

from .views import WebPushViewSet

app_name = "django_cfg_webpush"

# Create router
router = routers.DefaultRouter()

# Web Push API endpoints
router.register(r"", WebPushViewSet, basename="webpush")

urlpatterns = [
    # Include router URLs
    path("", include(router.urls)),
]
