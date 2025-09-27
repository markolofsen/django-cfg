"""
Subscription ViewSets for the Universal Payment System v2.0.

DRF ViewSets for subscription management with service integration.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from .base import PaymentBaseViewSet, NestedPaymentViewSet, ReadOnlyPaymentViewSet
from ...models import Subscription, EndpointGroup, Tariff
from ...services import get_subscription_service
from ..serializers.subscriptions import (
    SubscriptionSerializer,
    SubscriptionCreateSerializer,
    SubscriptionListSerializer,
    SubscriptionUpdateSerializer,
    SubscriptionUsageSerializer,
    SubscriptionStatsSerializer,
    EndpointGroupSerializer,
    TariffSerializer,
)
from django_cfg.modules.django_logger import get_logger

User = get_user_model()
logger = get_logger("subscription_viewsets")


class SubscriptionViewSet(PaymentBaseViewSet):
    """
    Global subscription ViewSet: /api/subscriptions/
    
    Provides admin-level access to all subscriptions with filtering and stats.
    """
    
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]  # Allow authenticated users
    filterset_fields = ['status', 'tier', 'user']
    search_fields = ['user__username', 'user__email']
    ordering_fields = ['created_at', 'updated_at', 'expires_at', 'total_requests']
    
    serializer_classes = {
        'list': SubscriptionListSerializer,
        'create': SubscriptionCreateSerializer,
        'retrieve': SubscriptionSerializer,
        'update': SubscriptionSerializer,
        'partial_update': SubscriptionSerializer,
    }
    
    def get_queryset(self):
        """Optimized queryset with related objects."""
        queryset = super().get_queryset().select_related(
            'user'
        ).prefetch_related(
            'endpoint_groups'
        )
        
        # Non-staff users can only see their own subscriptions
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        Update subscription status.
        
        POST /api/subscriptions/{id}/update_status/
        """
        subscription = self.get_object()
        
        serializer = SubscriptionUpdateSerializer(
            data=request.data,
            context={
                **self.get_serializer_context(),
                'subscription_id': str(subscription.id)
            }
        )
        
        if serializer.is_valid():
            result = serializer.save()
            return Response(result)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def increment_usage(self, request, pk=None):
        """
        Increment subscription usage.
        
        POST /api/subscriptions/{id}/increment_usage/
        """
        subscription = self.get_object()
        
        serializer = SubscriptionUsageSerializer(
            data=request.data,
            context={
                **self.get_serializer_context(),
                'subscription_id': str(subscription.id)
            }
        )
        
        if serializer.is_valid():
            result = serializer.save()
            return Response(result)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """
        Get subscription analytics.
        
        GET /api/subscriptions/analytics/?days=30
        """
        serializer = SubscriptionStatsSerializer(data=request.query_params)
        
        if serializer.is_valid():
            result = serializer.save()
            return Response(result)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """
        Get subscriptions grouped by status.
        
        GET /api/subscriptions/by_status/
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            status_stats = {}
            for status_choice in Subscription.SubscriptionStatus.choices:
                status_code = status_choice[0]
                status_name = status_choice[1]
                
                status_subscriptions = queryset.filter(status=status_code)
                
                status_stats[status_code] = {
                    'name': status_name,
                    'total_subscriptions': status_subscriptions.count(),
                    'total_requests': status_subscriptions.aggregate(
                        total=models.Sum('total_requests')
                    )['total'] or 0,
                    'active_users': status_subscriptions.values('user').distinct().count(),
                }
            
            return Response({
                'status_stats': status_stats,
                'generated_at': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Subscription status stats failed: {e}")
            return Response(
                {'error': f'Status stats failed: {e}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def by_tier(self, request):
        """
        Get subscriptions grouped by tier.
        
        GET /api/subscriptions/by_tier/
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            tier_stats = {}
            for tier_choice in Subscription.SubscriptionTier.choices:
                tier_code = tier_choice[0]
                tier_name = tier_choice[1]
                
                tier_subscriptions = queryset.filter(tier=tier_code)
                
                tier_stats[tier_code] = {
                    'name': tier_name,
                    'total_subscriptions': tier_subscriptions.count(),
                    'active_subscriptions': tier_subscriptions.filter(
                        status=Subscription.SubscriptionStatus.ACTIVE
                    ).count(),
                    'total_requests': tier_subscriptions.aggregate(
                        total=models.Sum('total_requests')
                    )['total'] or 0,
                }
            
            return Response({
                'tier_stats': tier_stats,
                'generated_at': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Subscription tier stats failed: {e}")
            return Response(
                {'error': f'Tier stats failed: {e}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserSubscriptionViewSet(NestedPaymentViewSet):
    """
    User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/
    
    Provides user-scoped access to subscriptions with full CRUD operations.
    """
    
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'tier']
    search_fields = []
    ordering_fields = ['created_at', 'updated_at', 'expires_at']
    
    # Nested ViewSet configuration
    parent_lookup_field = 'user_pk'
    parent_model_field = 'user'
    
    serializer_classes = {
        'list': SubscriptionListSerializer,
        'create': SubscriptionCreateSerializer,
        'retrieve': SubscriptionSerializer,
    }
    
    def get_queryset(self):
        """Filter by user and optimize queryset."""
        queryset = super().get_queryset()
        
        # Additional permission check: users can only see their own subscriptions
        if not self.request.user.is_staff:
            user_id = self.kwargs.get('user_pk')
            if str(self.request.user.id) != str(user_id):
                return queryset.none()
        
        return queryset.select_related('user').prefetch_related('endpoint_groups')
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, user_pk=None, pk=None):
        """
        Update subscription status.
        
        POST /api/users/{user_id}/subscriptions/{id}/update_status/
        """
        subscription = self.get_object()
        
        serializer = SubscriptionUpdateSerializer(
            data=request.data,
            context={
                **self.get_serializer_context(),
                'subscription_id': str(subscription.id)
            }
        )
        
        if serializer.is_valid():
            result = serializer.save()
            return Response(result)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def increment_usage(self, request, user_pk=None, pk=None):
        """
        Increment subscription usage.
        
        POST /api/users/{user_id}/subscriptions/{id}/increment_usage/
        """
        subscription = self.get_object()
        
        serializer = SubscriptionUsageSerializer(
            data=request.data,
            context={
                **self.get_serializer_context(),
                'subscription_id': str(subscription.id)
            }
        )
        
        if serializer.is_valid():
            result = serializer.save()
            return Response(result)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def active(self, request, user_pk=None):
        """
        Get user's active subscription.
        
        GET /api/users/{user_id}/subscriptions/active/
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            active_subscription = queryset.filter(
                status=Subscription.SubscriptionStatus.ACTIVE
            ).first()
            
            if active_subscription:
                serializer = self.get_serializer(active_subscription)
                return Response({
                    'success': True,
                    'subscription': serializer.data,
                    'message': 'Active subscription found'
                })
            else:
                return Response({
                    'success': False,
                    'subscription': None,
                    'message': 'No active subscription found'
                })
                
        except Exception as e:
            logger.error(f"Active subscription lookup failed: {e}")
            return Response(
                {'error': f'Active subscription lookup failed: {e}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def summary(self, request, user_pk=None):
        """
        Get user subscription summary.
        
        GET /api/users/{user_id}/subscriptions/summary/
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            summary = queryset.aggregate(
                total_subscriptions=models.Count('id'),
                active_subscriptions=models.Count(
                    'id',
                    filter=models.Q(status=Subscription.SubscriptionStatus.ACTIVE)
                ),
                expired_subscriptions=models.Count(
                    'id',
                    filter=models.Q(expires_at__lt=timezone.now())
                ),
                total_requests=models.Sum('total_requests'),
                requests_used=models.Sum('requests_used'),
            )
            
            return Response({
                'user_id': user_pk,
                'summary': {
                    **summary,
                    'total_requests': summary['total_requests'] or 0,
                    'requests_used': summary['requests_used'] or 0,
                    'requests_remaining': (summary['total_requests'] or 0) - (summary['requests_used'] or 0),
                },
                'generated_at': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"User subscription summary failed: {e}")
            return Response(
                {'error': f'Summary generation failed: {e}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EndpointGroupViewSet(ReadOnlyPaymentViewSet):
    """
    Endpoint Group ViewSet: /api/endpoint-groups/
    
    Read-only access to endpoint group information.
    """
    
    queryset = EndpointGroup.objects.filter(is_enabled=True)
    serializer_class = EndpointGroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['is_enabled']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        Get available endpoint groups for subscription.
        
        GET /api/endpoint-groups/available/
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            
            return Response({
                'endpoint_groups': serializer.data,
                'count': len(serializer.data),
                'generated_at': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Available endpoint groups failed: {e}")
            return Response(
                {'error': f'Available endpoint groups failed: {e}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TariffViewSet(ReadOnlyPaymentViewSet):
    """
    Tariff ViewSet: /api/tariffs/
    
    Read-only access to tariff information for subscription selection.
    """
    
    queryset = Tariff.objects.filter(is_active=True)
    serializer_class = TariffSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['monthly_price', 'requests_per_month', 'created_at']
    
    def get_queryset(self):
        """Optimize queryset with related objects."""
        return super().get_queryset().prefetch_related('endpoint_groups')
    
    @action(detail=False, methods=['get'])
    def free(self, request):
        """
        Get free tariffs.
        
        GET /api/tariffs/free/
        """
        free_tariffs = self.get_queryset().filter(monthly_price=0)
        serializer = self.get_serializer(free_tariffs, many=True)
        
        return Response({
            'tariffs': serializer.data,
            'count': len(serializer.data),
            'type': 'free',
            'generated_at': timezone.now().isoformat()
        })
    
    @action(detail=False, methods=['get'])
    def paid(self, request):
        """
        Get paid tariffs.
        
        GET /api/tariffs/paid/
        """
        paid_tariffs = self.get_queryset().filter(monthly_price__gt=0)
        serializer = self.get_serializer(paid_tariffs, many=True)
        
        return Response({
            'tariffs': serializer.data,
            'count': len(serializer.data),
            'type': 'paid',
            'generated_at': timezone.now().isoformat()
        })
    
    @action(detail=True, methods=['get'])
    def endpoint_groups(self, request, pk=None):
        """
        Get endpoint groups for specific tariff.
        
        GET /api/tariffs/{id}/endpoint_groups/
        """
        tariff = self.get_object()
        endpoint_groups = tariff.endpoint_groups.filter(is_active=True)
        serializer = EndpointGroupSerializer(endpoint_groups, many=True)
        
        return Response({
            'tariff': {
                'id': tariff.id,
                'name': tariff.name,
                'monthly_price': tariff.monthly_price,
            },
            'endpoint_groups': serializer.data,
            'count': len(serializer.data),
            'generated_at': timezone.now().isoformat()
        })
