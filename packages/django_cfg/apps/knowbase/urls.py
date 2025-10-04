"""
Knowledge Base URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DocumentViewSet, ChatViewSet, ChatSessionViewSet,
    DocumentArchiveViewSet, ArchiveItemViewSet, ArchiveItemChunkViewSet
)
from .views.public_views import PublicDocumentViewSet, PublicCategoryViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'chat', ChatViewSet, basename='chat')
router.register(r'sessions', ChatSessionViewSet, basename='session')

# Archive router for authenticated users
archive_router = DefaultRouter()
archive_router.register(r'archives', DocumentArchiveViewSet, basename='archive')
archive_router.register(r'items', ArchiveItemViewSet, basename='archive-item')
archive_router.register(r'chunks', ArchiveItemChunkViewSet, basename='archive-chunk')

# Public router for client access
public_router = DefaultRouter()
public_router.register(r'documents', PublicDocumentViewSet, basename='public-document')
public_router.register(r'categories', PublicCategoryViewSet, basename='public-category')

# URL patterns
urlpatterns = [
    # Admin API endpoints (require authentication + admin rights)
    path('admin/', include(router.urls)),
    
    # Archive API endpoints (require authentication)
    path('', include(archive_router.urls)),
    
    # Public API endpoints (no authentication required)
    path('public/', include(public_router.urls)),
]

# Add app name for namespacing
app_name = 'knowbase'
