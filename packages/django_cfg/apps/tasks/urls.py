"""
URLs for Django CFG Tasks app.

Provides RESTful endpoints for task queue management and monitoring using ViewSets and routers.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TaskManagementViewSet

app_name = 'tasks'

# Main router for ViewSets
router = DefaultRouter()
router.register(r'', TaskManagementViewSet, basename='task-management')

urlpatterns = [
    # RESTful API endpoints using ViewSets
    path('api/', include(router.urls)),

]
