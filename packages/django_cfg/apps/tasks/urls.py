"""
ReArq Tasks API URLs.

REST API endpoints for task monitoring and management.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import TaskLogViewSet

app_name = 'django_cfg_tasks'

router = DefaultRouter()
router.register(r'logs', TaskLogViewSet, basename='tasklog')

urlpatterns = router.urls
