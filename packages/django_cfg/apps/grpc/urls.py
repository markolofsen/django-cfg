"""
URL patterns for gRPC module.

Public API endpoints for gRPC monitoring.
"""

from django.urls import include, path
from rest_framework import routers

from .views.monitoring import GRPCMonitorViewSet

app_name = 'django_cfg_grpc'

# Create router
router = routers.DefaultRouter()

# Monitoring endpoints (Django logs based)
router.register(r'monitor', GRPCMonitorViewSet, basename='monitor')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
]
