"""
Subscription ViewSets with nested routing.
"""

from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from ..models import Subscription, EndpointGroup
from ..serializers import (
    SubscriptionSerializer, SubscriptionCreateSerializer, SubscriptionListSerializer,
    EndpointGroupSerializer
)

User = get_user_model()


class UserSubscriptionViewSet(viewsets.ModelViewSet):
    """Nested ViewSet for user subscriptions: /users/{user_id}/subscriptions/"""
    
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'tier', 'endpoint_group']
    
    def get_queryset(self):
        """Filter by user from URL."""
        user_id = self.kwargs.get('user_pk')
        return Subscription.objects.filter(user_id=user_id).order_by('-created_at')
    
    def get_serializer_class(self):
        """Use different serializers for different actions."""
        if self.action == 'create':
            return SubscriptionCreateSerializer
        elif self.action == 'list':
            return SubscriptionListSerializer
        return SubscriptionSerializer
    
    def perform_create(self, serializer):
        """Set user from URL when creating."""
        user_id = self.kwargs.get('user_pk')
        user = User.objects.get(id=user_id)
        serializer.save(user=user)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, user_pk=None, pk=None):
        """Cancel subscription."""
        subscription = self.get_object()
        subscription.status = 'cancelled'
        subscription.save()
        
        serializer = self.get_serializer(subscription)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def renew(self, request, user_pk=None, pk=None):
        """Renew subscription."""
        subscription = self.get_object()
        # TODO: Implement renewal logic
        return Response({'message': 'Subscription renewed'})
    
    @action(detail=False, methods=['get'])
    def active(self, request, user_pk=None):
        """Get active subscriptions for user."""
        queryset = self.get_queryset().filter(status='active')
        serializer = SubscriptionListSerializer(queryset, many=True)
        return Response(serializer.data)


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """Global subscription ViewSet: /subscriptions/"""
    
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'tier', 'endpoint_group']
    
    def get_queryset(self):
        """Filter by current user for security."""
        return Subscription.objects.filter(user=self.request.user).order_by('-created_at')
    
    def get_serializer_class(self):
        """Use list serializer for list action."""
        if self.action == 'list':
            return SubscriptionListSerializer
        return SubscriptionSerializer


class EndpointGroupViewSet(viewsets.ReadOnlyModelViewSet):
    """Endpoint groups ViewSet: /endpoint-groups/"""
    
    queryset = EndpointGroup.objects.filter(is_active=True)
    serializer_class = EndpointGroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def pricing(self, request, pk=None):
        """Get pricing for endpoint group."""
        endpoint_group = self.get_object()
        return Response({
            'basic_price': endpoint_group.basic_price,
            'premium_price': endpoint_group.premium_price,
            'enterprise_price': endpoint_group.enterprise_price,
            'basic_limit': endpoint_group.basic_limit,
            'premium_limit': endpoint_group.premium_limit,
            'enterprise_limit': endpoint_group.enterprise_limit,
        })


# Generic views for specific use cases
class SubscriptionCreateView(generics.CreateAPIView):
    """Generic view to create subscription."""
    
    serializer_class = SubscriptionCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        """Set current user when creating."""
        serializer.save(user=self.request.user)


class ActiveSubscriptionsView(generics.ListAPIView):
    """Generic view to list active subscriptions."""
    
    serializer_class = SubscriptionListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get active subscriptions for current user."""
        return Subscription.objects.filter(
            user=self.request.user,
            status='active'
        ).order_by('-created_at')
