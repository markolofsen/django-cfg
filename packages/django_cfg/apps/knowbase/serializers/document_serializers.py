"""
Document serializers for DRF API.
"""

from rest_framework import serializers
from typing import Dict, Any
from ..models import Document, ProcessingStatus


class DocumentCreateSerializer(serializers.Serializer):
    """Document creation request serializer."""
    
    title = serializers.CharField(
        max_length=512,
        help_text="Document title"
    )
    content = serializers.CharField(
        min_length=10,
        max_length=1_000_000,
        help_text="Document content"
    )
    file_type = serializers.RegexField(
        regex=r"^[a-z]+/[a-z0-9\-\+\.]+$",
        default="text/plain",
        help_text="MIME type"
    )
    metadata = serializers.JSONField(
        default=dict,
        help_text="Additional metadata"
    )
    
    def validate_content(self, value):
        """Validate content for security."""
        dangerous_patterns = [
            '<script', 'javascript:', 'data:',
            'vbscript:', 'onload=', 'onerror='
        ]
        
        if any(pattern in value.lower() for pattern in dangerous_patterns):
            raise serializers.ValidationError('Content contains potentially unsafe elements')
        
        return value
    
    def validate_title(self, value):
        """Validate title format."""
        if not value.strip():
            raise serializers.ValidationError('Title cannot be empty')
        return value.strip()


class DocumentSerializer(serializers.ModelSerializer):
    """Document response serializer."""
    
    id = serializers.UUIDField(read_only=True)
    processing_status = serializers.CharField(read_only=True)
    chunks_count = serializers.IntegerField(read_only=True)
    total_tokens = serializers.IntegerField(read_only=True)
    total_cost_usd = serializers.FloatField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    processing_started_at = serializers.DateTimeField(read_only=True)
    processing_completed_at = serializers.DateTimeField(read_only=True)
    processing_error = serializers.CharField(read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'file_type', 'file_size', 'processing_status',
            'chunks_count', 'total_tokens', 'total_cost_usd', 'created_at',
            'updated_at', 'processing_started_at', 'processing_completed_at',
            'processing_error', 'metadata'
        ]


class DocumentStatsSerializer(serializers.Serializer):
    """Document processing statistics serializer."""
    
    total_documents = serializers.IntegerField()
    completed_documents = serializers.IntegerField()
    processing_success_rate = serializers.FloatField()
    total_chunks = serializers.IntegerField()
    total_tokens = serializers.IntegerField()
    total_cost_usd = serializers.FloatField()
    avg_processing_time_seconds = serializers.FloatField()


class DocumentProcessingStatusSerializer(serializers.Serializer):
    """Document processing status serializer."""
    
    id = serializers.UUIDField()
    status = serializers.CharField()
    progress = serializers.JSONField()
    error = serializers.CharField(allow_null=True, required=False)
    processing_time_seconds = serializers.FloatField(allow_null=True, required=False)