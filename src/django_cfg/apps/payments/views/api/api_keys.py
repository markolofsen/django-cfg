"""
API Key ViewSets for the Universal Payment System v2.0.

DRF ViewSets for API key management with service integration.
"""

from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view

from .base import PaymentBaseViewSet, NestedPaymentViewSet, ReadOnlyPaymentViewSet
from ...models import APIKey
from ..serializers.api_keys import (
    APIKeySerializer,
    APIKeyCreateSerializer,
    APIKeyListSerializer,
    APIKeyUpdateSerializer,
    APIKeyActionSerializer,
    APIKeyValidationSerializer,
    APIKeyValidationResponseSerializer,
    APIKeyStatsSerializer,
)
from django_cfg.modules.django_logger import get_logger

User = get_user_model()
logger = get_logger("api_key_viewsets")


class APIKeyViewSet(PaymentBaseViewSet):
    """
    Global API Key ViewSet: /api/api-keys/
    
    Provides admin-level access to all API keys with filtering and stats.
    """
    
    queryset = APIKey.objects.all()
    serializer_class = APIKeySerializer
    permission_classes = [permissions.IsAdminUser]  # Admin only for global access
    filterset_fields = ['is_active', 'user']
    search_fields = ['name', 'user__username', 'user__email']
    ordering_fields = ['created_at', 'updated_at', 'last_used_at', 'expires_at', 'total_requests']
    
    serializer_classes = {
        'list': APIKeyListSerializer,
        'create': APIKeyCreateSerializer,
        'retrieve': APIKeySerializer,
        'update': APIKeyUpdateSerializer,
        'partial_update': APIKeyUpdateSerializer,
    }
    
    def get_queryset(self):
        """Optimized queryset with related objects."""
        return super().get_queryset().select_related('user')
    
    @action(detail=True, methods=['post'])
    def perform_action(self, request, pk=None):
        """
        Perform action on API key.
        
        POST /api/api-keys/{id}/perform_action/
        """
        api_key = self.get_object()
        
        serializer = APIKeyActionSerializer(
            data=request.data,
            context={
                **self.get_serializer_context(),
                'api_key_id': str(api_key.id)
            }
        )
        
        if serializer.is_valid():
            result = serializer.save()
            return Response(result)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary="Validate API Key",
        description="Validate an API key and return key information",
        request=APIKeyValidationSerializer,
        responses={200: APIKeyValidationResponseSerializer}
    )
    @action(detail=False, methods=['post'])
    def validate_key(self, request):
        """
        Validate API key.
        
        POST /api/api-keys/validate_key/
        """
        serializer = APIKeyValidationSerializer(
            data=request.data,
            context=self.get_serializer_context()
        )
        
        if serializer.is_valid():
            result = serializer.save()
            return Response(result)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """
        Get API key analytics.
        
        GET /api/api-keys/analytics/?days=30
        """
        serializer = APIKeyStatsSerializer(data=request.query_params)
        
        if serializer.is_valid():
            result = serializer.save()
            return Response(result)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def by_user(self, request):
        """
        Get API keys grouped by user.
        
        GET /api/api-keys/by_user/
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            user_stats = {}
            for api_key in queryset.select_related('user'):
                user_id = api_key.user.id
                username = api_key.user.username
                
                if user_id not in user_stats:
                    user_stats[user_id] = {
                        'user_id': user_id,
                        'username': username,
                        'total_keys': 0,
                        'active_keys': 0,
                        'expired_keys': 0,
                        'total_requests': 0,
                    }
                
                user_stats[user_id]['total_keys'] += 1
                if api_key.is_active:
                    user_stats[user_id]['active_keys'] += 1
                if api_key.is_expired():
                    user_stats[user_id]['expired_keys'] += 1
                user_stats[user_id]['total_requests'] += api_key.total_requests or 0
            
            return Response({
                'user_stats': list(user_stats.values()),
                'total_users': len(user_stats),
                'generated_at': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"API key user stats failed: {e}")
            return Response(
                {'error': f'User stats failed: {e}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """
        Get API keys expiring soon.
        
        GET /api/api-keys/expiring_soon/?days=7
        """
        try:
            days = int(request.query_params.get('days', 7))
            from datetime import timedelta
            
            expiry_threshold = timezone.now() + timedelta(days=days)
            
            queryset = self.filter_queryset(self.get_queryset())
            expiring_keys = queryset.filter(
                expires_at__lte=expiry_threshold,
                expires_at__gte=timezone.now(),
                is_active=True
            ).select_related('user')
            
            serializer = APIKeyListSerializer(expiring_keys, many=True)
            
            return Response({
                'expiring_keys': serializer.data,
                'count': len(serializer.data),
                'threshold_days': days,
                'generated_at': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Expiring API keys failed: {e}")
            return Response(
                {'error': f'Expiring keys lookup failed: {e}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserAPIKeyViewSet(NestedPaymentViewSet):
    """
    User-specific API Key ViewSet: /api/users/{user_id}/api-keys/
    
    Provides user-scoped access to API keys with full CRUD operations.
    """
    
    queryset = APIKey.objects.all()
    serializer_class = APIKeySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['is_active']
    search_fields = ['name']
    ordering_fields = ['created_at', 'updated_at', 'last_used_at', 'expires_at']
    
    # Nested ViewSet configuration
    parent_lookup_field = 'user_pk'
    parent_model_field = 'user'
    
    serializer_classes = {
        'list': APIKeyListSerializer,
        'create': APIKeyCreateSerializer,
        'retrieve': APIKeySerializer,
        'update': APIKeyUpdateSerializer,
        'partial_update': APIKeyUpdateSerializer,
    }
    
    def get_queryset(self):
        """Filter by user and optimize queryset."""
        queryset = super().get_queryset()
        
        # Additional permission check: users can only see their own API keys
        if not self.request.user.is_staff:
            user_id = self.kwargs.get('user_pk')
            if str(self.request.user.id) != str(user_id):
                return queryset.none()
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def perform_action(self, request, user_pk=None, pk=None):
        """
        Perform action on API key.
        
        POST /api/users/{user_id}/api-keys/{id}/perform_action/
        """
        api_key = self.get_object()
        
        serializer = APIKeyActionSerializer(
            data=request.data,
            context={
                **self.get_serializer_context(),
                'api_key_id': str(api_key.id)
            }
        )
        
        if serializer.is_valid():
            result = serializer.save()
            return Response(result)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def active(self, request, user_pk=None):
        """
        Get user's active API keys.
        
        GET /api/users/{user_id}/api-keys/active/
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            active_keys = queryset.filter(is_active=True)
            
            serializer = self.get_serializer(active_keys, many=True)
            
            return Response({
                'api_keys': serializer.data,
                'count': len(serializer.data),
                'user_id': user_pk,
                'generated_at': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Active API keys lookup failed: {e}")
            return Response(
                {'error': f'Active API keys lookup failed: {e}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def summary(self, request, user_pk=None):
        """
        Get user API key summary.
        
        GET /api/users/{user_id}/api-keys/summary/
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            summary = queryset.aggregate(
                total_keys=models.Count('id'),
                active_keys=models.Count('id', filter=models.Q(is_active=True)),
                expired_keys=models.Count('id', filter=models.Q(expires_at__lt=timezone.now())),
                total_requests=models.Sum('total_requests'),
                last_used=models.Max('last_used_at'),
            )
            
            return Response({
                'user_id': user_pk,
                'summary': {
                    **summary,
                    'total_requests': summary['total_requests'] or 0,
                    'inactive_keys': summary['total_keys'] - summary['active_keys'],
                    'last_used_formatted': summary['last_used'].isoformat() if summary['last_used'] else None,
                },
                'generated_at': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"User API key summary failed: {e}")
            return Response(
                {'error': f'Summary generation failed: {e}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Standalone views for common operations
class APIKeyCreateView(generics.CreateAPIView):
    """
    Standalone API key creation endpoint: /api/api-keys/create/
    
    Simplified endpoint for API key creation.
    """
    
    serializer_class = APIKeyCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """Create API key with enhanced response."""
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            try:
                api_key = serializer.save()
                
                response_data = {
                    'success': True,
                    'message': 'API key created successfully',
                    'api_key': serializer.to_representation(api_key)
                }
                
                return Response(response_data, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                logger.error(f"API key creation failed: {e}")
                return Response(
                    {
                        'success': False,
                        'error': f'API key creation failed: {e}',
                        'error_code': 'creation_failed'
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(
            {
                'success': False,
                'error': 'Invalid API key data',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class APIKeyValidateView(generics.GenericAPIView):
    """
    Standalone API key validation endpoint: /api/api-keys/validate/
    
    Quick validation without full ViewSet overhead.
    """
    
    serializer_class = APIKeyValidationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Validate API Key (Standalone)",
        description="Standalone endpoint to validate an API key and return key information",
        request=APIKeyValidationSerializer,
        responses={200: APIKeyValidationResponseSerializer}
    )
    def post(self, request, *args, **kwargs):
        """Validate API key."""
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            result = serializer.save()
            return Response(result)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
