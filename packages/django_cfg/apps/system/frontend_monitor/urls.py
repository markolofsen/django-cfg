"""
URL configuration for Frontend Monitor app.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api.views.ingest import FrontendMonitorViewSet

app_name = "cfg_frontend_monitor"

router = DefaultRouter()
router.register("", FrontendMonitorViewSet, basename="frontend-monitor")

urlpatterns = [
    path("", include(router.urls)),
]
