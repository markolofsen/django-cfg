"""
Public API views for client access without authentication.
"""

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import models
from drf_spectacular.utils import extend_schema, OpenApiParameter

from ..models import Document, DocumentCategory
from ..serializers.public_serializers import (
    PublicDocumentSerializer, 
    PublicDocumentListSerializer,
    PublicCategorySerializer
)


class PublicDocumentViewSet(viewsets.ReadOnlyModelViewSet):
    """Public document endpoints - read-only access for clients."""
    
    serializer_class = PublicDocumentSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'
    
    def get_queryset(self):
        """Get only publicly accessible documents."""
        return Document.objects.filter(
            processing_status='completed',
            is_public=True
        ).filter(
            models.Q(categories__isnull=True) | models.Q(categories__is_public=True)
        ).prefetch_related('categories')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return PublicDocumentListSerializer
        return PublicDocumentSerializer
    
    @extend_schema(
        summary="List public documents",
        description="Get list of all completed and publicly accessible documents",
        parameters=[
            OpenApiParameter(
                name='search',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Search in title and content'
            ),
            OpenApiParameter(
                name='category',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Filter by category name'
            ),
        ],
        responses={200: PublicDocumentListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """List all publicly accessible documents with optional filtering."""
        queryset = self.get_queryset()
        
        # Search functionality
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search) | 
                models.Q(content__icontains=search)
            )
        
        # Category filter
        category = request.query_params.get('category')
        if category:
            queryset = queryset.filter(categories__name__iexact=category)
        
        # Order by creation date (newest first)
        queryset = queryset.order_by('-created_at')
        
        # Use DRF pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get public document details",
        description="Get document details by ID (public access)",
        responses={
            200: PublicDocumentSerializer,
            404: "Document not found"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Get document by ID - public access."""
        return super().retrieve(request, *args, **kwargs)


class PublicCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Public category endpoints - read-only access for clients."""
    
    queryset = DocumentCategory.objects.filter(is_public=True)
    serializer_class = PublicCategorySerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'
    
    @extend_schema(
        summary="List public categories",
        description="Get list of all public categories",
        responses={200: PublicCategorySerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """List all public categories."""
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Get public category details",
        description="Get category details by ID (public access)",
        responses={
            200: PublicCategorySerializer,
            404: "Category not found"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Get category by ID - public access."""
        return super().retrieve(request, *args, **kwargs)
