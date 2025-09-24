"""
API key serializers.
"""

from rest_framework import serializers
from ..models import APIKey


class APIKeySerializer(serializers.ModelSerializer):
    """API key with usage stats."""
    
    is_valid = serializers.SerializerMethodField()
    
    class Meta:
        model = APIKey
        fields = [
            'id', 'name', 'key_value', 'key_prefix', 'usage_count',
            'is_active', 'is_valid', 'last_used', 'expires_at',
            'created_at'
        ]
        read_only_fields = ['key_value', 'key_prefix', 'usage_count', 'last_used', 'created_at']
    
    def get_is_valid(self, obj):
        """Get validation status."""
        return obj.is_valid()


class APIKeyCreateSerializer(serializers.ModelSerializer):
    """Create API key."""
    
    class Meta:
        model = APIKey
        fields = ['name', 'expires_at']


class APIKeyListSerializer(serializers.ModelSerializer):
    """Simplified API key for lists."""
    
    is_valid = serializers.SerializerMethodField()
    
    class Meta:
        model = APIKey
        fields = [
            'id', 'name', 'key_prefix', 'usage_count', 'is_active', 'is_valid',
            'last_used', 'expires_at', 'created_at'
        ]
        read_only_fields = ['key_prefix', 'usage_count', 'last_used', 'created_at']
    
    def get_is_valid(self, obj):
        """Get validation status."""
        return obj.is_valid()
