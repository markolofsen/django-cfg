"""
DRF Serializers for Users app.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile, UserActivity

User = get_user_model()


class UserActivitySerializer(serializers.ModelSerializer):
    """Serializer for user activities."""
    
    activity_type_display = serializers.CharField(source='get_activity_type_display', read_only=True)
    
    class Meta:
        model = UserActivity
        fields = [
            'id', 'activity_type', 'activity_type_display', 'description',
            'ip_address', 'object_id', 'object_type', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profiles."""
    
    class Meta:
        model = UserProfile
        fields = [
            'website', 'github', 'twitter', 'linkedin',
            'company', 'job_title', 'posts_count', 'comments_count',
            'orders_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['posts_count', 'comments_count', 'orders_count', 'created_at', 'updated_at']


class UserListSerializer(serializers.ModelSerializer):
    """Serializer for user list view."""
    
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'is_active', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined']


class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer for user detail view."""
    
    full_name = serializers.CharField(read_only=True)
    profile = UserProfileSerializer(read_only=True)
    activities = UserActivitySerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'bio', 'location', 'birth_date', 'avatar',
            'is_public', 'email_notifications', 'is_active',
            'date_joined', 'created_at', 'updated_at',
            'profile', 'activities'
        ]
        read_only_fields = ['id', 'username', 'date_joined', 'created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for user creation."""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password', 'password_confirm'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Create profile
        UserProfile.objects.create(user=user)
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for user updates."""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'bio', 'location', 'birth_date',
            'avatar', 'is_public', 'email_notifications'
        ]


class UserStatsSerializer(serializers.Serializer):
    """Serializer for user statistics."""
    
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    new_users_today = serializers.IntegerField()
    new_users_this_week = serializers.IntegerField()
    new_users_this_month = serializers.IntegerField()
    top_users = UserListSerializer(many=True)
