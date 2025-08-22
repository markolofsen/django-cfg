"""
URL configuration for Users app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import UserViewSet, UserActivityViewSet

# Main router
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'activities', UserActivityViewSet, basename='activity')

# Nested router for user activities
users_router = routers.NestedDefaultRouter(router, r'users', lookup='user')
users_router.register(r'activities', UserActivityViewSet, basename='user-activities')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(users_router.urls)),
]
