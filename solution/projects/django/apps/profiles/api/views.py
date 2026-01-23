"""DRF Views for Profiles app."""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.profiles.models import UserProfile
from apps.profiles.api.serializers import (
    UserProfileSerializer, UserProfileUpdateSerializer, UserProfileStatsSerializer
)

User = get_user_model()


@extend_schema_view(
    list=extend_schema(
        summary="List user profiles",
        description="Get a paginated list of all user profiles",
        tags=["Profiles"]
    ),
    create=extend_schema(
        summary="Create user profile",
        description="Create a new user profile",
        tags=["Profiles"]
    ),
    retrieve=extend_schema(
        summary="Get user profile",
        description="Get detailed information about a specific user profile",
        tags=["Profiles"]
    ),
    update=extend_schema(
        summary="Update user profile",
        description="Update user profile information",
        tags=["Profiles"]
    ),
    partial_update=extend_schema(
        summary="Partially update user profile",
        description="Partially update user profile information",
        tags=["Profiles"]
    ),
    destroy=extend_schema(
        summary="Delete user profile",
        description="Delete a user profile",
        tags=["Profiles"]
    ),
)
class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user profiles.

    Provides CRUD operations for user profiles with automatic creation via signals.
    """

    queryset = UserProfile.objects.select_related('user')
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UserProfileUpdateSerializer
        return UserProfileSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by user
        user_id = self.request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # Search by company or job title
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(company__icontains=search) |
                Q(job_title__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__username__icontains=search)
            )

        return queryset

    def perform_create(self, serializer):
        """Ensure profile is created for the current user."""
        serializer.save(user=self.request.user)

    @extend_schema(
        summary="Get profile statistics",
        description="Get comprehensive profile statistics",
        responses={200: UserProfileStatsSerializer},
        tags=["Profiles"]
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get profile statistics."""
        stats = {
            'total_profiles': UserProfile.objects.count(),
            'profiles_with_company': UserProfile.objects.exclude(company='').count(),
            'profiles_with_social_links': UserProfile.objects.filter(
                Q(website__isnull=False) | Q(github__isnull=False) |
                Q(twitter__isnull=False) | Q(linkedin__isnull=False)
            ).exclude(
                Q(website='') & Q(github='') & Q(twitter='') & Q(linkedin='')
            ).count(),
            'most_active_users': UserProfile.objects.annotate(
                total_activity=Count('posts_count') + Count('comments_count') + Count('orders_count')
            ).order_by('-posts_count', '-comments_count', '-orders_count')[:10]
        }

        serializer = UserProfileStatsSerializer(stats)
        return Response(serializer.data)

    @extend_schema(
        summary="Get my profile",
        description="Get current user's profile",
        responses={200: UserProfileSerializer},
        tags=["Profiles"]
    )
    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """Get or update current user's profile."""
        profile, created = UserProfile.objects.get_or_create(user=request.user)

        if request.method == 'GET':
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)

        elif request.method in ['PUT', 'PATCH']:
            partial = request.method == 'PATCH'
            serializer = UserProfileUpdateSerializer(profile, data=request.data, partial=partial)
            if serializer.is_valid():
                serializer.save()
                # Return full profile data
                full_serializer = UserProfileSerializer(profile)
                return Response(full_serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
