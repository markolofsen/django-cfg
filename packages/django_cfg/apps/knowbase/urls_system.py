"""
Knowledge Base URL Configuration
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ArchiveItemChunkViewSet, ArchiveItemViewSet, DocumentArchiveViewSet

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
