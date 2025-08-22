"""
DRF Views for Users app.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import UserProfile, UserActivity
from .serializers import (
    UserListSerializer, UserDetailSerializer, UserCreateSerializer,
    UserUpdateSerializer, UserProfileSerializer, UserActivitySerializer,
    UserStatsSerializer
)

User = get_user_model()


@extend_schema_view(
    list=extend_schema(
        summary="List users",
        description="Get a paginated list of all users",
        tags=["Users"]
    ),
    create=extend_schema(
        summary="Create user",
        description="Create a new user account",
        tags=["Users"]
    ),
    retrieve=extend_schema(
        summary="Get user",
        description="Get detailed information about a specific user",
        tags=["Users"]
    ),
    update=extend_schema(
        summary="Update user",
        description="Update user information",
        tags=["Users"]
    ),
    partial_update=extend_schema(
        summary="Partially update user",
        description="Partially update user information",
        tags=["Users"]
    ),
    destroy=extend_schema(
        summary="Delete user",
        description="Delete a user account",
        tags=["Users"]
    ),
)
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users.
    
    Provides CRUD operations for users with nested profile and activity data.
    """
    
    queryset = User.objects.select_related('profile').prefetch_related('activities')
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        else:
            return UserDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Search by name or email
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(username__icontains=search)
            )
        
        return queryset
    
    @extend_schema(
        summary="Get user statistics",
        description="Get comprehensive user statistics",
        responses={200: UserStatsSerializer},
        tags=["Users"]
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get user statistics."""
        now = timezone.now()
        today = now.date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        stats = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'new_users_today': User.objects.filter(date_joined__date=today).count(),
            'new_users_this_week': User.objects.filter(date_joined__date__gte=week_ago).count(),
            'new_users_this_month': User.objects.filter(date_joined__date__gte=month_ago).count(),
            'top_users': User.objects.annotate(
                activity_count=Count('activities')
            ).order_by('-activity_count')[:10]
        }
        
        serializer = UserStatsSerializer(stats)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get user profile",
        description="Get detailed profile information for a user",
        responses={200: UserProfileSerializer},
        tags=["Users"]
    )
    @action(detail=True, methods=['get', 'put', 'patch'])
    def profile(self, request, pk=None):
        """Get or update user profile."""
        user = self.get_object()
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        if request.method == 'GET':
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            partial = request.method == 'PATCH'
            serializer = UserProfileSerializer(profile, data=request.data, partial=partial)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary="Get user activities",
        description="Get activity log for a user",
        responses={200: UserActivitySerializer(many=True)},
        tags=["Users"]
    )
    @action(detail=True, methods=['get'])
    def activities(self, request, pk=None):
        """Get user activities."""
        user = self.get_object()
        activities = user.activities.all()[:50]  # Last 50 activities
        
        # Filter by activity type
        activity_type = request.query_params.get('type')
        if activity_type:
            activities = activities.filter(activity_type=activity_type)
        
        serializer = UserActivitySerializer(activities, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Deactivate user",
        description="Deactivate a user account",
        tags=["Users"]
    )
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate user."""
        user = self.get_object()
        user.is_active = False
        user.save()
        
        # Log activity
        UserActivity.objects.create(
            user=user,
            activity_type='logout',
            description='Account deactivated',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return Response({'status': 'User deactivated'})
    
    @extend_schema(
        summary="Activate user",
        description="Activate a user account",
        tags=["Users"]
    )
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate user."""
        user = self.get_object()
        user.is_active = True
        user.save()
        
        # Log activity
        UserActivity.objects.create(
            user=user,
            activity_type='login',
            description='Account activated',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return Response({'status': 'User activated'})


@extend_schema_view(
    list=extend_schema(
        summary="List user activities",
        description="Get a list of all user activities",
        tags=["User Activities"]
    ),
    retrieve=extend_schema(
        summary="Get activity",
        description="Get details of a specific activity",
        tags=["User Activities"]
    ),
)
class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for user activities (read-only).
    """
    
    queryset = UserActivity.objects.select_related('user')
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by user
        user_id = self.request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by activity type
        activity_type = self.request.query_params.get('type')
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
        
        return queryset
