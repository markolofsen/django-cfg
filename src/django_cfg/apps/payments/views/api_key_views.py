"""
API Key ViewSets with nested routing.
"""

from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from ..models import APIKey
from ..serializers import (
    APIKeySerializer, APIKeyCreateSerializer, APIKeyListSerializer
)

User = get_user_model()


class UserAPIKeyViewSet(viewsets.ModelViewSet):
    """Nested ViewSet for user API keys: /users/{user_id}/api-keys/"""
    
    serializer_class = APIKeySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active']
    
    def get_queryset(self):
        """Filter by user from URL."""
        user_id = self.kwargs.get('user_pk')
        return APIKey.objects.filter(user_id=user_id).order_by('-created_at')
    
    def get_serializer_class(self):
        """Use different serializers for different actions."""
        if self.action == 'create':
            return APIKeyCreateSerializer
        elif self.action == 'list':
            return APIKeyListSerializer
        return APIKeySerializer
    
    def perform_create(self, serializer):
        """Set user from URL when creating."""
        user_id = self.kwargs.get('user_pk')
        user = User.objects.get(id=user_id)
        
        # Generate unique API key
        import secrets
        key_value = f"ak_{secrets.token_urlsafe(32)}"
        
        serializer.save(user=user, key_value=key_value)
    
    @action(detail=True, methods=['post'])
    def regenerate(self, request, user_pk=None, pk=None):
        """Regenerate API key."""
        api_key = self.get_object()
        
        # Generate new key
        import secrets
        api_key.key_value = f"ak_{secrets.token_urlsafe(32)}"
        api_key.usage_count = 0  # Reset usage
        api_key.save()
        
        serializer = self.get_serializer(api_key)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, user_pk=None, pk=None):
        """Deactivate API key."""
        api_key = self.get_object()
        api_key.is_active = False
        api_key.save()
        
        return Response({'message': 'API key deactivated'})
    
    @action(detail=True, methods=['get'])
    def usage_stats(self, request, user_pk=None, pk=None):
        """Get usage statistics for API key."""
        api_key = self.get_object()
        
        return Response({
            'usage_count': api_key.usage_count,
            'last_used': api_key.last_used,
            'is_valid': api_key.is_valid(),
            'expires_at': api_key.expires_at,
            'is_active': api_key.is_active,
        })


class APIKeyViewSet(viewsets.ReadOnlyModelViewSet):
    """Global API keys ViewSet: /api-keys/"""
    
    queryset = APIKey.objects.all()
    serializer_class = APIKeySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active']
    
    def get_queryset(self):
        """Filter by current user for security."""
        return APIKey.objects.filter(user=self.request.user).order_by('-created_at')
    
    def get_serializer_class(self):
        """Use list serializer for list action."""
        if self.action == 'list':
            return APIKeyListSerializer
        return APIKeySerializer


# Generic views for specific use cases
class APIKeyCreateView(generics.CreateAPIView):
    """Generic view to create API key."""
    
    serializer_class = APIKeyCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        """Set current user and generate key when creating."""
        import secrets
        key_value = f"ak_{secrets.token_urlsafe(32)}"
        serializer.save(user=self.request.user, key_value=key_value)


class APIKeyValidateView(generics.GenericAPIView):
    """Generic view to validate API key."""
    
    serializer_class = APIKeySerializer  # For schema generation
    permission_classes = [permissions.AllowAny]  # Public endpoint
    
    def post(self, request):
        """Validate API key."""
        key_value = request.data.get('api_key')
        
        if not key_value:
            return Response(
                {'error': 'API key required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            api_key = APIKey.objects.get(key_value=key_value, is_active=True)
            
            # Check if expired
            if api_key.is_expired:
                return Response(
                    {'error': 'API key expired'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Update last used
            from django.utils import timezone
            api_key.last_used = timezone.now()
            api_key.save()
            
            return Response({
                'valid': True,
                'user_id': api_key.user.id,
                'usage_count': api_key.usage_count,
                'expires_at': api_key.expires_at,
                'is_active': api_key.is_active,
            })
            
        except APIKey.DoesNotExist:
            return Response(
                {'valid': False, 'error': 'Invalid API key'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
