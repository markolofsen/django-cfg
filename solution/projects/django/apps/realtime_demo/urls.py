"""URL configuration for the realtime demo (mounted by its OpenAPIGroupConfig, not by api/urls.py)."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.realtime_demo.api import DemoPingViewSet

router = DefaultRouter()
router.register(r"pings", DemoPingViewSet, basename="pings")

urlpatterns = [
    path("", include(router.urls)),
]
