"""
URL patterns for gRPC module.

Public API endpoints for gRPC monitoring.
"""

from django.urls import include, path
from rest_framework import routers

from .views.api_keys import GRPCApiKeyViewSet
from .views.charts import GRPCChartsViewSet
from .views.config import GRPCConfigViewSet
from .views.monitoring import GRPCMonitorViewSet
from .views.proto_files import GRPCProtoFilesViewSet
from .views.services import GRPCServiceViewSet
from .views.testing import GRPCTestingViewSet

app_name = 'django_cfg_grpc'

# Create router
router = routers.DefaultRouter()

# Monitoring endpoints (Django logs based)
router.register(r'monitor', GRPCMonitorViewSet, basename='monitor')

# Configuration endpoints
router.register(r'config', GRPCConfigViewSet, basename='config')

# Service registry endpoints
router.register(r'services', GRPCServiceViewSet, basename='services')

# Testing endpoints
router.register(r'test', GRPCTestingViewSet, basename='test')

# Charts endpoints (statistics visualization)
router.register(r'charts', GRPCChartsViewSet, basename='charts')

# API Keys endpoints (read-only)
router.register(r'api-keys', GRPCApiKeyViewSet, basename='api-keys')

# Proto Files endpoints (download proto files)
router.register(r'proto-files', GRPCProtoFilesViewSet, basename='proto-files')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
]
