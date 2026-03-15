"""
django_monitor URL configuration.

Mounted at: /cfg/monitor/
OpenAPI group: cfg_monitor
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api.views import MonitorIngestViewSet

app_name = "cfg_monitor"

router = DefaultRouter()
router.register("", MonitorIngestViewSet, basename="monitor")

urlpatterns = [
    path("", include(router.urls)),
]
