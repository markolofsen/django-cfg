"""
URL patterns for Centrifugo module.

Public API endpoints for Centrifugo monitoring and admin API proxy.
"""

from django.urls import include, path
from rest_framework import routers

from .views.admin_api import CentrifugoAdminAPIViewSet
from .views.monitoring import CentrifugoMonitorViewSet
from .views.testing_api import CentrifugoTestingAPIViewSet

app_name = 'django_cfg_centrifugo'

# Create router
router = routers.DefaultRouter()

# Monitoring endpoints (Django logs based)
router.register(r'monitor', CentrifugoMonitorViewSet, basename='monitor')

# Admin API proxy endpoints (Centrifugo server based)
router.register(r'server', CentrifugoAdminAPIViewSet, basename='server')

# Testing API endpoints (live testing from dashboard)
router.register(r'testing', CentrifugoTestingAPIViewSet, basename='testing')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
]
