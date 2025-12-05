"""
URL patterns for Centrifugo module.

Public API endpoints for Centrifugo monitoring, admin API proxy, and RPC proxy.
"""

from django.urls import include, path
from rest_framework import routers

from .views.admin_api import CentrifugoAdminAPIViewSet
from .views.monitoring import CentrifugoMonitorViewSet
from .views.rpc_proxy import RPCProxyView
from .views.testing_api import CentrifugoTestingAPIViewSet
from .views.token_api import CentrifugoTokenViewSet
from .views.wrapper import PublishWrapperView

app_name = 'django_cfg_centrifugo'

# Create router
router = routers.DefaultRouter()

# Monitoring endpoints (Django logs based)
router.register(r'monitor', CentrifugoMonitorViewSet, basename='monitor')

# Admin API proxy endpoints (Centrifugo server based)
router.register(r'server', CentrifugoAdminAPIViewSet, basename='server')

# Testing API endpoints (live testing from dashboard)
router.register(r'testing', CentrifugoTestingAPIViewSet, basename='testing')

# Token API endpoints (JWT token generation for client connections)
router.register(r'auth', CentrifugoTokenViewSet, basename='auth')

urlpatterns = [
    # RPC Proxy endpoint (for Centrifugo RPC calls)
    # Centrifugo forwards client.rpc() calls to this endpoint
    path('rpc/', RPCProxyView.as_view(), name='rpc_proxy'),

    # Wrapper API endpoint (for CentrifugoClient publish)
    path('api/publish', PublishWrapperView.as_view(), name='wrapper_publish'),

    # Include router URLs
    path('', include(router.urls)),
]
