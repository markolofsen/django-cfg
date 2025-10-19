"""
URL patterns for IPC/RPC module.

Public API endpoints for RPC monitoring using DRF router.
"""

from django.urls import include, path
from rest_framework import routers

from .views.viewsets import RPCMonitorViewSet

app_name = 'django_cfg_ipc'

# Create router
router = routers.DefaultRouter()
router.register(r'monitor', RPCMonitorViewSet, basename='monitor')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
]
