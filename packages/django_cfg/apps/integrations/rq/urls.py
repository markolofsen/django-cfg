"""
URL patterns for Django-RQ monitoring and management API.

Public API endpoints for RQ task queue monitoring, job management,
queue management, worker monitoring, and schedule management.

Endpoints:
    /rq/monitor/         - Monitoring, health checks, and metrics
    /rq/queues/          - Queue management (list, details, empty)
    /rq/workers/         - Worker monitoring and statistics
    /rq/jobs/            - Job management (view, cancel, requeue, delete)
    /rq/schedules/       - Schedule management (create, list, cancel)
    /rq/testing/         - Testing and simulation (demo tasks, stress tests)
"""

from django.urls import include, path
from rest_framework import routers

from .views import (
    RQMonitorViewSet,
    QueueViewSet,
    WorkerViewSet,
    JobViewSet,
    ScheduleViewSet,
    TestingViewSet,
)

app_name = 'django_cfg_rq'

# Create router
router = routers.DefaultRouter()

# Monitoring endpoints (health, config, metrics)
router.register(r'monitor', RQMonitorViewSet, basename='monitor')

# Queue management endpoints
router.register(r'queues', QueueViewSet, basename='queues')

# Worker monitoring endpoints
router.register(r'workers', WorkerViewSet, basename='workers')

# Job management endpoints
router.register(r'jobs', JobViewSet, basename='jobs')

# Schedule management endpoints (requires rq-scheduler)
router.register(r'schedules', ScheduleViewSet, basename='schedules')

# Testing and simulation endpoints (admin-only)
router.register(r'testing', TestingViewSet, basename='testing')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
]
