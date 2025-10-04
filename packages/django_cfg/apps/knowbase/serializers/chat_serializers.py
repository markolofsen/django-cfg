"""
Chat serializers for DRF API.
"""

from rest_framework import serializers
from ..models import ChatSession, ChatMessage
from ..utils.validation import is_valid_float, safe_float


class ChatSessionCreateSerializer(serializers.Serializer):
    """Chat session creation request serializer."""
    
    title = serializers.CharField(
        max_length=255,
        default="",
        allow_blank=True,
        help_text="Session title"
    )
    model_name = serializers.CharField(
        max_length=100,
        default="openai/gpt-4o-mini",
        help_text="LLM model to use"
    )
    temperature = serializers.FloatField(
        min_value=0.0,
        max_value=2.0,
        default=0.7,
        help_text="Response creativity"
    )
    max_context_chunks = serializers.IntegerField(
        min_value=1,
        max_value=10,
        default=5,
        help_text="Maximum context chunks"
    )


class ChatQuerySerializer(serializers.Serializer):
    """Chat query request serializer."""
    
    session_id = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text="Chat session ID (creates new if not provided)"
    )
    query = serializers.CharField(
        min_length=1,
        max_length=2000,
        help_text="User query"
    )
    max_tokens = serializers.IntegerField(
        min_value=1,
        max_value=4000,
        default=1000,
        help_text="Maximum response tokens"
    )
    include_sources = serializers.BooleanField(
        default=True,
        help_text="Include source documents in response"
    )
    
    def validate_query(self, value):
        """Validate query content."""
        if not value.strip():
            raise serializers.ValidationError('Query cannot be empty')
        return value.strip()


class ChatSourceSerializer(serializers.Serializer):
    """Chat source document information serializer."""
    
    document_title = serializers.CharField()
    chunk_content = serializers.CharField()
    similarity = serializers.FloatField()
    
    def validate_similarity(self, value):
        """Validate similarity value to prevent NaN in JSON."""
        if not is_valid_float(value):
            raise serializers.ValidationError('Invalid similarity value')
        return value


class ChatResponseSerializer(serializers.Serializer):
    """Chat response serializer."""
    
    message_id = serializers.UUIDField()
    content = serializers.CharField()
    tokens_used = serializers.IntegerField()
    cost_usd = serializers.FloatField()
    processing_time_ms = serializers.IntegerField()
    model_used = serializers.CharField()
    sources = ChatSourceSerializer(many=True, required=False, allow_null=True)


class ChatSessionSerializer(serializers.ModelSerializer):
    """Chat session response serializer."""
    
    id = serializers.UUIDField(read_only=True)
    total_cost_usd = serializers.FloatField(read_only=True)
    
    def validate_total_cost_usd(self, value):
        """Validate cost value to prevent NaN in JSON."""
        return safe_float(value, 0.0)
    
    class Meta:
        model = ChatSession
        fields = [
            'id', 'title', 'is_active', 'messages_count', 'total_tokens_used',
            'total_cost_usd', 'model_name', 'temperature', 'max_context_chunks',
            'created_at', 'updated_at'
        ]


class ChatMessageSerializer(serializers.ModelSerializer):
    """Chat message response serializer."""
    
    id = serializers.UUIDField(read_only=True)
    cost_usd = serializers.FloatField(read_only=True)
    
    def validate_cost_usd(self, value):
        """Validate cost value to prevent NaN in JSON."""
        return safe_float(value, 0.0)
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'role', 'content', 'tokens_used', 'cost_usd',
            'processing_time_ms', 'created_at', 'context_chunks'
        ]


class ChatHistorySerializer(serializers.Serializer):
    """Chat history response serializer."""
    
    session_id = serializers.UUIDField()
    messages = ChatMessageSerializer(many=True)
    total_messages = serializers.IntegerField()