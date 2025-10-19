"""
Knowledge Base URL Configuration
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ChatSessionViewSet,
    ChatViewSet,
    DocumentViewSet,
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'chat', ChatViewSet, basename='chat')
router.register(r'sessions', ChatSessionViewSet, basename='session')

# URL patterns
urlpatterns = [
    # Admin API endpoints (require authentication + admin rights)
    path('', include(router.urls)),
]

app_name = 'cfg_knowbase_admin'
