"""
Knowledge Base URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DocumentArchiveViewSet, ArchiveItemViewSet, ArchiveItemChunkViewSet
)

# Archive router for authenticated users
archive_router = DefaultRouter()
archive_router.register(r'archives', DocumentArchiveViewSet, basename='archive')
archive_router.register(r'items', ArchiveItemViewSet, basename='archive-item')
archive_router.register(r'chunks', ArchiveItemChunkViewSet, basename='archive-chunk')

# URL patterns
urlpatterns = [

    # Archive API endpoints (require authentication)
    path('', include(archive_router.urls)),
    
]

# Add app name for namespacing
app_name = 'cfg_knowbase_system'
