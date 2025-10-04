"""
Document management API views.
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.db import models
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter

from ..models import Document
from ..services import DocumentService
from ..serializers import (
    DocumentCreateSerializer,
    DocumentSerializer,
    DocumentStatsSerializer,
    DocumentProcessingStatusSerializer
)
from .base import BaseKnowledgeViewSet


class DocumentViewSet(BaseKnowledgeViewSet):
    """Document management endpoints - Admin only."""
    
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    service_class = DocumentService
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return DocumentCreateSerializer
        elif self.action == 'stats':
            return DocumentStatsSerializer
        elif self.action == 'status':
            return DocumentProcessingStatusSerializer
        return DocumentSerializer
    
    @extend_schema(
        summary="Upload new document",
        description="Upload and process a new knowledge document",
        responses={
            201: DocumentSerializer,
            400: "Validation errors",
            413: "File too large",
            429: "Rate limit exceeded"
        },
        examples=[
            OpenApiExample(
                "Text Document",
                value={
                    "title": "API Documentation",
                    "content": "# API Guide\n\nThis guide explains...",
                    "file_type": "text/markdown"
                }
            )
        ]
    )
    @method_decorator(ratelimit(key='user', rate='10/m', method='POST'))
    def create(self, request, *args, **kwargs):
        """Create new document with async processing."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Use service layer for business logic
        service = self.get_service()
        document = service.create_document(
            title=serializer.validated_data['title'],
            content=serializer.validated_data['content'],
            file_type=serializer.validated_data['file_type'],
            metadata=serializer.validated_data['metadata']
        )
        
        response_serializer = DocumentSerializer(document)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="List user documents",
        parameters=[
            OpenApiParameter(
                name='status',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Filter by processing status'
            ),
        ],
        responses={200: DocumentSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """List user documents with filtering and pagination."""
        status_filter = request.query_params.get('status')
        
        service = self.get_service()
        queryset = service.get_user_documents(status=status_filter)
        
        # Use DRF pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get document details",
        responses={
            200: DocumentSerializer,
            404: "Document not found"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Get document by ID."""
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete document",
        responses={
            204: "Document deleted successfully",
            404: "Document not found"
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Delete document and all associated chunks."""
        return super().destroy(request, *args, **kwargs)
    
    @extend_schema(
        summary="Get document processing status",
        responses={200: DocumentProcessingStatusSerializer}
    )
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get document processing status."""
        document = self.get_object()
        
        data = {
            'id': document.id,
            'status': document.processing_status,
            'progress': {
                'chunks_processed': document.chunks_count,
                'total_tokens': document.total_tokens,
                'processing_time': document.processing_duration
            },
            'error': document.processing_error if document.processing_error else None,
            'processing_time_seconds': document.processing_duration
        }
        
        serializer = self.get_serializer(data)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Reprocess document",
        description="Trigger reprocessing of document chunks and embeddings"
    )
    @action(detail=True, methods=['post'])
    def reprocess(self, request, pk=None):
        """Trigger document reprocessing."""
        document = self.get_object()
        
        service = self.get_service()
        service.reprocess_document(str(document.id))
        
        return Response({
            'message': 'Document reprocessing started',
            'document_id': str(document.id)
        })
    
    @extend_schema(
        summary="Get processing statistics",
        responses={200: DocumentStatsSerializer}
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get user's document processing statistics."""
        service = self.get_service()
        stats = service.get_processing_stats()
        
        serializer = self.get_serializer(stats)
        return Response(serializer.data)