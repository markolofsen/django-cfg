"""URL configuration for Profiles app."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.profiles.api import UserProfileViewSet

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet, basename='Profiles')

urlpatterns = [
    path('', include(router.urls)),
]
