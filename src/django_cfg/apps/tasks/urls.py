"""
URLs for Django CFG Tasks app.

Provides RESTful endpoints for task queue management and monitoring using ViewSets and routers.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'tasks'

# Main router for ViewSets
router = DefaultRouter()
router.register(r'', views.TaskManagementViewSet, basename='task-management')

urlpatterns = [
    # RESTful API endpoints using ViewSets
    path('api/', include(router.urls)),
    
]
