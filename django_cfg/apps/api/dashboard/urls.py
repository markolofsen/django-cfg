"""
Dashboard URLs

RESTful API endpoints for dashboard data organized by domain.

API Structure:
- /api/overview/ - Complete dashboard overview
- /api/statistics/ - Statistics endpoints (cards, users, apps)
- /api/system/ - System monitoring (health, metrics)
- /api/activity/ - Activity tracking (recent, actions)
- /api/config/ - Configuration (DjangoConfig, Django settings)
- /api/metrics/ - Universal metrics (LLM balances, system health, API stats)
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    OverviewViewSet,
    StatisticsViewSet,
    SystemViewSet,
    ActivityViewSet,
    ChartsViewSet,
    CommandsViewSet,
    APIZonesViewSet,
    ConfigViewSet,
    MetricsViewSet,
)

app_name = 'django_cfg_dashboard'

# Main router for ViewSets
router = DefaultRouter()
router.register(r'overview', OverviewViewSet, basename='overview')
router.register(r'statistics', StatisticsViewSet, basename='statistics')
router.register(r'system', SystemViewSet, basename='system')
router.register(r'activity', ActivityViewSet, basename='activity')
router.register(r'charts', ChartsViewSet, basename='charts')
router.register(r'commands', CommandsViewSet, basename='commands')
router.register(r'zones', APIZonesViewSet, basename='zones')
router.register(r'config', ConfigViewSet, basename='config')
router.register(r'metrics', MetricsViewSet, basename='metrics')

urlpatterns = [
    # RESTful API endpoints using ViewSets
    # Mounted at /cfg/dashboard/api/
    path('api/', include(router.urls)),
]
