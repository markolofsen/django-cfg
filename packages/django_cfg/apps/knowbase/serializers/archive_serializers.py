"""
Archive serializers for DRF API.
"""

from rest_framework import serializers
from typing import Dict, Any, List
from ..models.archive import DocumentArchive, ArchiveItem, ArchiveItemChunk, ArchiveType, ContentType, ChunkType
from ..models.document import DocumentCategory


class DocumentArchiveCreateSerializer(serializers.Serializer):
    """Document archive creation request serializer."""
    
    archive_file = serializers.FileField(
        help_text="Archive file to upload"
    )
    title = serializers.CharField(
        max_length=512,
        required=False,
        help_text="Archive title (auto-generated from filename if not provided)"
    )
    description = serializers.CharField(
        max_length=2000,
        required=False,
        allow_blank=True,
        help_text="Archive description"
    )
    category_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        default=list,
        help_text="List of category IDs"
    )
    is_public = serializers.BooleanField(
        default=True,
        help_text="Whether archive is publicly accessible"
    )
    process_immediately = serializers.BooleanField(
        default=True,
        help_text="Process archive synchronously"
    )
    
    def validate_archive_file(self, value):
        """Validate uploaded archive file."""
        if not value:
            raise serializers.ValidationError('Archive file is required')
        
        # Check file size (max 100MB)
        max_size = 100 * 1024 * 1024  # 100MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f'File too large. Maximum size is {max_size // (1024*1024)}MB'
            )
        
        # Check file extension
        allowed_extensions = [
            '.zip', '.jar', '.war', '.ear',  # ZIP formats
            '.tar.gz', '.tgz',               # TAR.GZ formats
            '.tar.bz2', '.tbz2', '.tar.bzip2',  # TAR.BZ2 formats
            '.tar'                           # TAR formats
        ]
        filename = value.name.lower()
        if not any(filename.endswith(ext) for ext in allowed_extensions):
            raise serializers.ValidationError(
                f'Unsupported file format. Allowed: {", ".join(allowed_extensions)}'
            )
        
        return value
    
    def validate_title(self, value: str) -> str:
        """Validate title format."""
        if value and not value.strip():
            raise serializers.ValidationError('Title cannot be empty')
        return value.strip() if value else value
    
    def validate_category_ids(self, value: List[str]) -> List[str]:
        """Validate category IDs exist."""
        if value:
            existing_ids = set(
                DocumentCategory.objects.filter(
                    id__in=value
                ).values_list('id', flat=True)
            )
            
            invalid_ids = set(str(id) for id in value) - set(str(id) for id in existing_ids)
            if invalid_ids:
                raise serializers.ValidationError(
                    f'Invalid category IDs: {", ".join(invalid_ids)}'
                )
        
        return value


class DocumentCategorySerializer(serializers.ModelSerializer):
    """Document category serializer."""
    
    class Meta:
        model = DocumentCategory
        fields = ['id', 'name', 'description', 'is_public', 'created_at']
        read_only_fields = ['id', 'created_at']


class ArchiveItemSerializer(serializers.ModelSerializer):
    """Archive item serializer."""
    
    class Meta:
        model = ArchiveItem
        fields = [
            'id', 'relative_path', 'item_name', 'item_type', 'content_type',
            'file_size', 'is_processable', 'language', 'encoding',
            'chunks_count', 'total_tokens', 'processing_cost',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'content_type', 'is_processable', 'language', 'encoding',
            'chunks_count', 'total_tokens', 'processing_cost',
            'created_at', 'updated_at'
        ]


class ArchiveItemDetailSerializer(ArchiveItemSerializer):
    """Detailed archive item serializer with content."""
    
    raw_content = serializers.CharField(read_only=True)
    metadata = serializers.JSONField(read_only=True)
    
    class Meta(ArchiveItemSerializer.Meta):
        fields = ArchiveItemSerializer.Meta.fields + ['raw_content', 'metadata']


class ArchiveItemChunkSerializer(serializers.ModelSerializer):
    """Archive item chunk serializer."""
    
    context_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = ArchiveItemChunk
        fields = [
            'id', 'content', 'chunk_index', 'chunk_type',
            'token_count', 'character_count', 'embedding_model',
            'embedding_cost', 'context_summary', 'created_at'
        ]
        read_only_fields = [
            'id', 'token_count', 'character_count', 'embedding_model',
            'embedding_cost', 'context_summary', 'created_at'
        ]
    
    def get_context_summary(self, obj: ArchiveItemChunk) -> Dict[str, Any]:
        """Get context summary for display."""
        return obj.get_context_summary()


class ArchiveItemChunkDetailSerializer(ArchiveItemChunkSerializer):
    """Detailed chunk serializer with full context."""
    
    context_metadata = serializers.JSONField(read_only=True)
    
    class Meta(ArchiveItemChunkSerializer.Meta):
        fields = ArchiveItemChunkSerializer.Meta.fields + ['context_metadata']


class DocumentArchiveSerializer(serializers.ModelSerializer):
    """Document archive serializer."""
    
    categories = DocumentCategorySerializer(many=True, read_only=True)
    processing_progress = serializers.ReadOnlyField()
    vectorization_progress = serializers.ReadOnlyField()
    is_processed = serializers.ReadOnlyField()
    
    class Meta:
        model = DocumentArchive
        fields = [
            'id', 'title', 'description', 'categories', 'is_public',
            'archive_file', 'original_filename', 'file_size', 'archive_type',
            'processing_status', 'processed_at', 'processing_duration_ms',
            'processing_error', 'total_items', 'processed_items',
            'total_chunks', 'vectorized_chunks', 'total_tokens',
            'total_cost_usd', 'processing_progress', 'vectorization_progress',
            'is_processed', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'original_filename', 'file_size', 'archive_type',
            'processing_status', 'processed_at', 'processing_duration_ms',
            'processing_error', 'total_items', 'processed_items',
            'total_chunks', 'vectorized_chunks', 'total_tokens',
            'total_cost_usd', 'processing_progress', 'vectorization_progress',
            'is_processed', 'created_at', 'updated_at'
        ]


class DocumentArchiveDetailSerializer(DocumentArchiveSerializer):
    """Detailed archive serializer with items."""
    
    items = ArchiveItemSerializer(many=True, read_only=True)
    file_tree = serializers.SerializerMethodField()
    
    class Meta(DocumentArchiveSerializer.Meta):
        fields = DocumentArchiveSerializer.Meta.fields + ['items', 'file_tree', 'metadata']
    
    def get_file_tree(self, obj: DocumentArchive) -> Dict[str, Any]:
        """Get hierarchical file tree."""
        return obj.get_file_tree()


class DocumentArchiveListSerializer(serializers.ModelSerializer):
    """Simplified archive serializer for list views."""
    
    categories = DocumentCategorySerializer(many=True, read_only=True)
    processing_progress = serializers.ReadOnlyField()
    
    class Meta:
        model = DocumentArchive
        fields = [
            'id', 'title', 'description', 'categories', 'is_public',
            'original_filename', 'file_size', 'archive_type',
            'processing_status', 'processed_at', 'total_items',
            'total_chunks', 'total_cost_usd', 'processing_progress',
            'created_at'
        ]
        read_only_fields = fields


class ArchiveProcessingResultSerializer(serializers.Serializer):
    """Archive processing result serializer."""
    
    archive_id = serializers.UUIDField(read_only=True)
    status = serializers.CharField(read_only=True)
    processing_time_ms = serializers.IntegerField(read_only=True)
    items_processed = serializers.IntegerField(read_only=True)
    chunks_created = serializers.IntegerField(read_only=True)
    vectorized_chunks = serializers.IntegerField(read_only=True)
    total_cost_usd = serializers.FloatField(read_only=True)
    error_message = serializers.CharField(read_only=True, required=False)


class ArchiveSearchRequestSerializer(serializers.Serializer):
    """Archive search request serializer."""
    
    query = serializers.CharField(
        min_length=1,
        max_length=500,
        help_text="Search query"
    )
    content_types = serializers.MultipleChoiceField(
        choices=ContentType.choices,
        required=False,
        help_text="Filter by content types"
    )
    languages = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        help_text="Filter by programming languages"
    )
    chunk_types = serializers.MultipleChoiceField(
        choices=ChunkType.choices,
        required=False,
        help_text="Filter by chunk types"
    )
    archive_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        help_text="Search within specific archives"
    )
    limit = serializers.IntegerField(
        min_value=1,
        max_value=50,
        default=10,
        help_text="Maximum number of results"
    )
    similarity_threshold = serializers.FloatField(
        min_value=0.0,
        max_value=1.0,
        default=0.7,
        help_text="Minimum similarity threshold"
    )


class ArchiveSearchResultSerializer(serializers.Serializer):
    """Archive search result serializer."""
    
    chunk = ArchiveItemChunkSerializer(read_only=True)
    similarity_score = serializers.FloatField(read_only=True)
    context_summary = serializers.DictField(read_only=True)
    archive_info = serializers.DictField(read_only=True)
    item_info = serializers.DictField(read_only=True)


class ArchiveStatisticsSerializer(serializers.Serializer):
    """Archive statistics serializer."""
    
    total_archives = serializers.IntegerField(read_only=True)
    processed_archives = serializers.IntegerField(read_only=True)
    failed_archives = serializers.IntegerField(read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_chunks = serializers.IntegerField(read_only=True)
    total_tokens = serializers.IntegerField(read_only=True)
    total_cost = serializers.FloatField(read_only=True)
    avg_processing_time = serializers.FloatField(read_only=True)
    avg_items_per_archive = serializers.FloatField(read_only=True)
    avg_chunks_per_archive = serializers.FloatField(read_only=True)


class VectorizationStatisticsSerializer(serializers.Serializer):
    """Vectorization statistics serializer."""
    
    total_chunks = serializers.IntegerField(read_only=True)
    vectorized_chunks = serializers.IntegerField(read_only=True)
    pending_chunks = serializers.IntegerField(read_only=True)
    vectorization_rate = serializers.FloatField(read_only=True)
    total_tokens = serializers.IntegerField(read_only=True)
    total_cost = serializers.FloatField(read_only=True)
    avg_tokens_per_chunk = serializers.FloatField(read_only=True)
    avg_cost_per_chunk = serializers.FloatField(read_only=True)


class ContentTypeDistributionSerializer(serializers.Serializer):
    """Content type distribution serializer."""
    
    content_type = serializers.CharField(read_only=True)
    count = serializers.IntegerField(read_only=True)
    percentage = serializers.FloatField(read_only=True)


class LanguageDistributionSerializer(serializers.Serializer):
    """Language distribution serializer."""
    
    language = serializers.CharField(read_only=True)
    count = serializers.IntegerField(read_only=True)
    percentage = serializers.FloatField(read_only=True)


class ArchiveUploadSerializer(serializers.Serializer):
    """Archive file upload serializer."""
    
    file = serializers.FileField(
        help_text="Archive file to upload"
    )
    
    def validate_file(self, value):
        """Validate uploaded file."""
        
        # Check file size (200MB limit)
        max_size = 200 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(
                f'File too large. Maximum size is {max_size // (1024*1024)}MB'
            )
        
        # Check file extension
        allowed_extensions = ['.zip', '.tar', '.tar.gz', '.tgz', '.tar.bz2', '.tbz2']
        filename = value.name.lower()
        
        if not any(filename.endswith(ext) for ext in allowed_extensions):
            raise serializers.ValidationError(
                f'Unsupported file type. Allowed: {", ".join(allowed_extensions)}'
            )
        
        return value


class ChunkRevectorizationRequestSerializer(serializers.Serializer):
    """Chunk re-vectorization request serializer."""
    
    chunk_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        help_text="List of chunk IDs to re-vectorize"
    )
    force = serializers.BooleanField(
        default=False,
        help_text="Force re-vectorization even if already vectorized"
    )


class VectorizationResultSerializer(serializers.Serializer):
    """Vectorization result serializer."""
    
    vectorized_count = serializers.IntegerField(read_only=True)
    failed_count = serializers.IntegerField(read_only=True)
    total_tokens = serializers.IntegerField(read_only=True)
    total_cost = serializers.FloatField(read_only=True)
    success_rate = serializers.FloatField(read_only=True)
    errors = serializers.ListField(
        child=serializers.CharField(),
        read_only=True
    )
