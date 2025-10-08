"""
DRF Serializers for Profiles app.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile
from typing import Any, Dict

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profiles."""
    
    user_info = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'user_info', 'website', 'github', 'twitter', 'linkedin',
            'company', 'job_title', 'posts_count', 'comments_count',
            'orders_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'posts_count', 'comments_count', 'orders_count', 'created_at', 'updated_at']
    
    def get_user_info(self, obj) -> Dict[str, Any]:
        """Get basic user information."""
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'email': obj.user.email,
            'full_name': obj.user.full_name if hasattr(obj.user, 'full_name') else f"{obj.user.first_name} {obj.user.last_name}".strip(),
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
        }


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profiles."""
    
    class Meta:
        model = UserProfile
        fields = [
            'website', 'github', 'twitter', 'linkedin',
            'company', 'job_title'
        ]


class UserProfileStatsSerializer(serializers.Serializer):
    """Serializer for profile statistics."""
    
    total_profiles = serializers.IntegerField()
    profiles_with_company = serializers.IntegerField()
    profiles_with_social_links = serializers.IntegerField()
    most_active_users = UserProfileSerializer(many=True)
