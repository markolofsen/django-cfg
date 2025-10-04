"""
Knowledge Base Serializers

Pydantic v2 models for API request/response validation.
"""

from .document_serializers import *
from .chat_serializers import *
from .public_serializers import *
from .archive_serializers import *
from .external_data_serializers import *

__all__ = [
    # Document serializers
    'DocumentCreateSerializer',
    'DocumentSerializer',
    'DocumentStatsSerializer',
    'DocumentProcessingStatusSerializer',
    
    # Public serializers
    'PublicCategorySerializer',
    'PublicDocumentListSerializer',
    'PublicDocumentSerializer',
    
    # Chat serializers
    'ChatSessionCreateRequest',
    'ChatSessionResponse',
    'ChatQueryRequest',
    'ChatResponse',
    'ChatHistoryResponse',
    
    # Archive serializers
    'DocumentArchiveCreateSerializer',
    'DocumentArchiveSerializer',
    'DocumentArchiveDetailSerializer',
    'DocumentArchiveListSerializer',
    'ArchiveItemSerializer',
    'ArchiveItemDetailSerializer',
    'ArchiveItemChunkSerializer',
    'ArchiveItemChunkDetailSerializer',
    'ArchiveProcessingResultSerializer',
    'ArchiveSearchRequestSerializer',
    'ArchiveSearchResultSerializer',
    'ArchiveStatisticsSerializer',
    'VectorizationStatisticsSerializer',
    'ArchiveUploadSerializer',
    'ChunkRevectorizationRequestSerializer',
    'VectorizationResultSerializer',
    
    # External data serializers
    'ExternalDataCreateRequest',
    'ExternalDataResponse',
    'ExternalDataListResponse',
    'ExternalDataChunkResponse',
    'ExternalDataSearchRequest',
    'ExternalDataSearchResult',
    'ExternalDataSearchResponse',
    'ExternalDataVectorizeRequest',
    'ExternalDataVectorizeResponse',
    'ExternalDataStatsResponse',
    'ExternalDataHealthResponse',
    'ExternalDataUpdateRequest',
    'ExternalDataBulkActionRequest',
    'ExternalDataBulkActionResponse',
    'ExternalDataQuickAddRequest',
    'ExternalDataImportRequest',
    'ExternalDataImportResponse',
]
