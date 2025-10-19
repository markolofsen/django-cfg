"""
Knowledge Base URL Configuration
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views.public_views import PublicCategoryViewSet, PublicDocumentViewSet

# Public router for client access
public_router = DefaultRouter()
public_router.register(r'documents', PublicDocumentViewSet, basename='public-document')
public_router.register(r'categories', PublicCategoryViewSet, basename='public-category')

# URL patterns
urlpatterns = [

    # Public API endpoints (no authentication required)
    path('', include(public_router.urls)),
]

# Add app name for namespacing
app_name = 'cfg_knowbase'
