"""
Document archive management API views.
"""

from rest_framework import status, viewsets, parsers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.db import models
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from typing import Dict, Any
import logging

from ..models.archive import DocumentArchive, ArchiveItem, ArchiveItemChunk
from ..services.archive import (
    DocumentArchiveService, 
    ArchiveVectorizationService,
    ArchiveProcessingError,
    ArchiveValidationError
)
from ..serializers.archive_serializers import (
    DocumentArchiveCreateSerializer,
    DocumentArchiveSerializer,
    DocumentArchiveDetailSerializer,
    DocumentArchiveListSerializer,
    ArchiveItemSerializer,
    ArchiveItemDetailSerializer,
    ArchiveItemChunkSerializer,
    ArchiveItemChunkDetailSerializer,
    ArchiveProcessingResultSerializer,
    ArchiveSearchRequestSerializer,
    ArchiveSearchResultSerializer,
    ArchiveStatisticsSerializer,
    VectorizationStatisticsSerializer,
    ArchiveUploadSerializer,
    ChunkRevectorizationRequestSerializer,
    VectorizationResultSerializer
)
from .base import BaseKnowledgeViewSet

logger = logging.getLogger(__name__)


class DocumentArchiveViewSet(BaseKnowledgeViewSet):
    """Document archive management endpoints - Admin only."""
    
    queryset = DocumentArchive.objects.all()
    serializer_class = DocumentArchiveSerializer
    service_class = DocumentArchiveService
    permission_classes = [IsAuthenticated, IsAdminUser]
    parser_classes = [parsers.MultiPartParser, parsers.JSONParser]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return DocumentArchiveCreateSerializer
        elif self.action == 'list':
            return DocumentArchiveListSerializer
        elif self.action in ['retrieve', 'items', 'file_tree']:
            return DocumentArchiveDetailSerializer
        elif self.action == 'upload':
            return ArchiveUploadSerializer
        elif self.action == 'processing_result':
            return ArchiveProcessingResultSerializer
        elif self.action == 'statistics':
            return ArchiveStatisticsSerializer
        return DocumentArchiveSerializer
    
    @extend_schema(
        summary="Upload and process archive",
        description="Upload archive file and process it synchronously",
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'file': {'type': 'string', 'format': 'binary'},
                    'title': {'type': 'string'},
                    'description': {'type': 'string'},
                    'category_ids': {'type': 'array', 'items': {'type': 'string'}},
                    'is_public': {'type': 'boolean'},
                    'process_immediately': {'type': 'boolean'}
                }
            }
        },
        responses={
            201: ArchiveProcessingResultSerializer,
            400: "Validation errors",
            413: "File too large",
            429: "Rate limit exceeded"
        }
    )
    @method_decorator(ratelimit(key='user', rate='5/hour', method='POST'))
    def create(self, request, *args, **kwargs):
        """Upload and process archive file."""
        
        # Validate file upload
        file_serializer = ArchiveUploadSerializer(data=request.FILES)
        if not file_serializer.is_valid():
            return Response(
                file_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate metadata
        metadata_serializer = DocumentArchiveCreateSerializer(data=request.data)
        if not metadata_serializer.is_valid():
            return Response(
                metadata_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            service = self.get_service()
            uploaded_file = file_serializer.validated_data['file']
            
            # Process archive
            result = service.create_and_process_archive(
                uploaded_file=uploaded_file,
                request_data=metadata_serializer.validated_data
            )
            
            # Return processing result
            result_serializer = ArchiveProcessingResultSerializer(result)
            return Response(
                result_serializer.data,
                status=status.HTTP_201_CREATED
            )
            
        except ArchiveValidationError as e:
            return Response(
                {
                    'error': 'Validation Error',
                    'message': e.message,
                    'code': e.code,
                    'details': e.details
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except ArchiveProcessingError as e:
            return Response(
                {
                    'error': 'Processing Error',
                    'message': e.message,
                    'code': e.code,
                    'details': e.details
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Archive upload error: {e}", exc_info=True)
            return Response(
                {
                    'error': 'Internal Server Error',
                    'message': 'An unexpected error occurred'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Get archive items",
        description="Get all items in the archive",
        responses={200: ArchiveItemSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """Get archive items."""
        
        archive = self.get_object()
        items = archive.items.all().order_by('relative_path')
        
        serializer = ArchiveItemSerializer(items, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get archive file tree",
        description="Get hierarchical file tree structure",
        responses={200: {'type': 'object'}}
    )
    @action(detail=True, methods=['get'])
    def file_tree(self, request, pk=None):
        """Get archive file tree structure."""
        
        archive = self.get_object()
        file_tree = archive.get_file_tree()
        
        return Response({'file_tree': file_tree})
    
    @extend_schema(
        summary="Search archive chunks",
        description="Semantic search within archive chunks",
        request=ArchiveSearchRequestSerializer,
        responses={200: ArchiveSearchResultSerializer(many=True)}
    )
    @action(detail=True, methods=['post'])
    def search(self, request, pk=None):
        """Search within archive chunks."""
        
        archive = self.get_object()
        
        # Validate search request
        search_serializer = ArchiveSearchRequestSerializer(data=request.data)
        if not search_serializer.is_valid():
            return Response(
                search_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        search_data = search_serializer.validated_data
        
        try:
            # Perform search using vectorization service
            vectorization_service = ArchiveVectorizationService(request.user)
            
            # Generate query embedding
            from django_cfg.modules.django_llm.llm.client import LLMClient
            from django_cfg.apps.knowbase.config.settings import get_openai_api_key, get_openrouter_api_key, get_cache_settings
            cache_settings = get_cache_settings()
            llm_client = LLMClient(
                apikey_openai=get_openai_api_key(),
                apikey_openrouter=get_openrouter_api_key(),
                cache_dir=cache_settings.cache_dir,
                cache_ttl=cache_settings.cache_ttl,
                max_cache_size=cache_settings.max_cache_size
            )
            # Generate query embedding with specified model
            from django_cfg.apps.knowbase.utils.chunk_settings import get_embedding_model
            embedding_model = get_embedding_model()
            embedding_result = llm_client.generate_embedding(
                text=search_data['query'],
                model=embedding_model
            )
            
            # Search chunks using manager's semantic_search method
            chunks = ArchiveItemChunk.objects.semantic_search(
                query_embedding=embedding_result.embedding,
                limit=search_data.get('limit', 10),
                similarity_threshold=search_data.get('similarity_threshold', 0.7),
                content_types=search_data.get('content_types'),
                languages=search_data.get('languages'),
                # Filter by archive and user
                archive=archive,
                user=request.user,
                chunk_types=search_data.get('chunk_types')
            )
            
            # Build search results
            results = []
            for chunk in chunks:
                result_data = {
                    'chunk': chunk,
                    'similarity_score': getattr(chunk, 'similarity', 0.0),
                    'context_summary': chunk.get_context_summary(),
                    'archive_info': {
                        'id': str(archive.id),
                        'title': archive.title
                    },
                    'item_info': {
                        'id': str(chunk.item.id),
                        'relative_path': chunk.item.relative_path,
                        'content_type': chunk.item.content_type
                    }
                }
                results.append(result_data)
            
            serializer = ArchiveSearchResultSerializer(results, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Archive search error: {e}", exc_info=True)
            return Response(
                {'error': 'Search failed', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Get archive statistics",
        description="Get processing and vectorization statistics",
        responses={200: ArchiveStatisticsSerializer}
    )
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get user's archive statistics."""
        
        service = self.get_service()
        
        # Get archive statistics from manager
        from ..managers.archive import DocumentArchiveManager
        archive_manager = DocumentArchiveManager()
        archive_manager.model = DocumentArchive
        
        stats = archive_manager.get_processing_statistics(user=request.user)
        
        serializer = ArchiveStatisticsSerializer(stats)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get vectorization statistics",
        description="Get vectorization statistics for archives",
        responses={200: VectorizationStatisticsSerializer}
    )
    @action(detail=False, methods=['get'])
    def vectorization_stats(self, request):
        """Get vectorization statistics."""
        
        vectorization_service = ArchiveVectorizationService(request.user)
        stats = vectorization_service.get_vectorization_statistics()
        
        serializer = VectorizationStatisticsSerializer(stats)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Re-vectorize chunks",
        description="Re-vectorize specific chunks",
        request=ChunkRevectorizationRequestSerializer,
        responses={200: VectorizationResultSerializer}
    )
    @action(detail=False, methods=['post'])
    def revectorize(self, request):
        """Re-vectorize specific chunks."""
        
        serializer = ChunkRevectorizationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            vectorization_service = ArchiveVectorizationService(request.user)
            result = vectorization_service.revectorize_chunks(
                chunk_ids=serializer.validated_data['chunk_ids'],
                force=serializer.validated_data['force']
            )
            
            result_serializer = VectorizationResultSerializer(result)
            return Response(result_serializer.data)
            
        except Exception as e:
            logger.error(f"Re-vectorization error: {e}", exc_info=True)
            return Response(
                {'error': 'Re-vectorization failed', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ArchiveItemViewSet(BaseKnowledgeViewSet):
    """Archive item management endpoints - Admin only."""
    
    queryset = ArchiveItem.objects.all()
    serializer_class = ArchiveItemSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        """Filter items by user and optional archive."""
        queryset = super().get_queryset()
        
        archive_id = self.request.query_params.get('archive_id')
        if archive_id:
            queryset = queryset.filter(archive_id=archive_id)
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['retrieve', 'content']:
            return ArchiveItemDetailSerializer
        return ArchiveItemSerializer
    
    @extend_schema(
        summary="Get item content",
        description="Get full content of archive item",
        responses={200: ArchiveItemDetailSerializer}
    )
    @action(detail=True, methods=['get'])
    def content(self, request, pk=None):
        """Get item content."""
        
        item = self.get_object()
        serializer = ArchiveItemDetailSerializer(item)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get item chunks",
        description="Get all chunks for this item",
        responses={200: ArchiveItemChunkSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def chunks(self, request, pk=None):
        """Get item chunks."""
        
        item = self.get_object()
        chunks = item.chunks.all().order_by('chunk_index')
        
        serializer = ArchiveItemChunkSerializer(chunks, many=True)
        return Response(serializer.data)


class ArchiveItemChunkViewSet(BaseKnowledgeViewSet):
    """Archive item chunk management endpoints - Admin only."""
    
    queryset = ArchiveItemChunk.objects.all()
    serializer_class = ArchiveItemChunkSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        """Filter chunks by user and optional filters."""
        queryset = super().get_queryset()
        
        # Filter by archive
        archive_id = self.request.query_params.get('archive_id')
        if archive_id:
            queryset = queryset.filter(archive_id=archive_id)
        
        # Filter by item
        item_id = self.request.query_params.get('item_id')
        if item_id:
            queryset = queryset.filter(item_id=item_id)
        
        # Filter by chunk type
        chunk_type = self.request.query_params.get('chunk_type')
        if chunk_type:
            queryset = queryset.filter(chunk_type=chunk_type)
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['retrieve', 'context']:
            return ArchiveItemChunkDetailSerializer
        return ArchiveItemChunkSerializer
    
    @extend_schema(
        summary="Get chunk context",
        description="Get full context metadata for chunk",
        responses={200: ArchiveItemChunkDetailSerializer}
    )
    @action(detail=True, methods=['get'])
    def context(self, request, pk=None):
        """Get chunk context metadata."""
        
        chunk = self.get_object()
        serializer = ArchiveItemChunkDetailSerializer(chunk)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Vectorize chunk",
        description="Generate embedding for specific chunk",
        responses={200: {'type': 'object'}}
    )
    @action(detail=True, methods=['post'])
    def vectorize(self, request, pk=None):
        """Vectorize specific chunk."""
        
        chunk = self.get_object()
        
        try:
            vectorization_service = ArchiveVectorizationService(request.user)
            result = vectorization_service.vectorize_single_chunk(str(chunk.id))
            
            return Response(result)
            
        except Exception as e:
            logger.error(f"Chunk vectorization error: {e}", exc_info=True)
            return Response(
                {'error': 'Vectorization failed', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
