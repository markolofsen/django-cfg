"""
URL configuration for Profiles app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserProfileViewSet

# Main router
router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet, basename='Profiles')

urlpatterns = [
    path('', include(router.urls)),
]
