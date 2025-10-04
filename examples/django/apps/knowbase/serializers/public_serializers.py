"""
Public serializers for client access without sensitive data.
"""

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from ..models import Document, DocumentCategory


class PublicCategorySerializer(serializers.ModelSerializer):
    """Public category serializer."""
    
    id = serializers.UUIDField(read_only=True)
    
    class Meta:
        model = DocumentCategory
        fields = ['id', 'name', 'description']


class PublicDocumentListSerializer(serializers.ModelSerializer):
    """Public document list serializer - minimal fields for listing."""
    
    id = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    category = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'category', 'created_at', 'updated_at'
        ]
    
    @extend_schema_field(PublicCategorySerializer)
    def get_category(self, obj):
        """Get first public category or create a default one."""
        public_categories = obj.categories.filter(is_public=True)
        if public_categories.exists():
            return PublicCategorySerializer(public_categories.first()).data
        # Return default category if no public categories
        return {
            'id': None,
            'name': 'General',
            'description': 'General documentation'
        }


class PublicDocumentSerializer(serializers.ModelSerializer):
    """Public document detail serializer - only essential data for clients."""
    
    id = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    category = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'content', 'category', 'created_at', 'updated_at'
        ]
        # Only essential fields for clients - no technical metadata
    
    @extend_schema_field(PublicCategorySerializer)
    def get_category(self, obj):
        """Get first public category or create a default one."""
        public_categories = obj.categories.filter(is_public=True)
        if public_categories.exists():
            return PublicCategorySerializer(public_categories.first()).data
        # Return default category if no public categories
        return {
            'id': None,
            'name': 'General',
            'description': 'General documentation'
        }
