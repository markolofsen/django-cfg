"""
URL patterns for gRPC module.

Public API endpoints for gRPC monitoring.
"""

from django.urls import include, path
from rest_framework import routers

from .views import (
    GRPCApiKeyViewSet,
    GRPCConfigViewSet,
    GRPCMonitorViewSet,
    GRPCServiceViewSet,
)

app_name = 'django_cfg_grpc'

# Create router
router = routers.DefaultRouter()

# Monitoring endpoints (Django logs based)
router.register(r'monitor', GRPCMonitorViewSet, basename='monitor')

# Configuration endpoints
router.register(r'config', GRPCConfigViewSet, basename='config')

# Service registry endpoints
router.register(r'services', GRPCServiceViewSet, basename='services')

# API Keys endpoints (read-only)
router.register(r'api-keys', GRPCApiKeyViewSet, basename='api-keys')

urlpatterns = [
    path('', include(router.urls)),
]
