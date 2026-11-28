"""DRF Serializers for Profiles app."""

from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.profiles.models import UserProfile

User = get_user_model()


class UserInfoSerializer(serializers.Serializer):
    """Stable nested wire shape for the profile's user summary."""

    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True, allow_blank=True)
    full_name = serializers.SerializerMethodField()
    first_name = serializers.CharField(read_only=True, allow_blank=True)
    last_name = serializers.CharField(read_only=True, allow_blank=True)

    @extend_schema_field(serializers.CharField(allow_blank=True))
    def get_full_name(self, user) -> str:
        value = getattr(user, "full_name", None)
        return value if value is not None else f"{user.first_name} {user.last_name}".strip()


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profiles."""

    user_info = UserInfoSerializer(source="user", read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'user_info', 'website', 'github', 'twitter', 'linkedin',
            'company', 'job_title', 'posts_count', 'comments_count',
            'orders_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'posts_count', 'comments_count', 'orders_count', 'created_at', 'updated_at']

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
