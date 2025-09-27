"""
Base ViewSet classes for the Universal Payment System v2.0.

Common functionality for all payment system ViewSets.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.exceptions import NotFound

from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
from typing import Dict, Any

from django_cfg.modules.django_logger import get_logger

logger = get_logger("api_viewsets")


class PaymentBaseViewSet(viewsets.ModelViewSet):
    """
    Enhanced base ViewSet with common functionality.
    
    Provides standard CRUD operations plus common actions like stats,
    health checks, and optimized querysets.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering = ['-created_at']
    versioning_class = None  # Disable versioning for payments API
    
    # Serializer classes mapping for different actions
    serializer_classes = {}
    
    def get_queryset(self):
        """
        Optimized queryset with select_related and prefetch_related.
        
        Override in subclasses to add specific optimizations.
        """
        queryset = super().get_queryset()
        
        # Add common optimizations
        if hasattr(self.queryset.model, 'user'):
            queryset = queryset.select_related('user')
        
        return queryset
    
    def get_serializer_class(self):
        """
        Dynamic serializer selection based on action.
        
        Uses serializer_classes mapping or falls back to default.
        """
        serializer_classes = getattr(self, 'serializer_classes', {})
        return serializer_classes.get(self.action, self.serializer_class)
    
    def get_serializer_context(self):
        """
        Enhanced serializer context with additional data.
        """
        context = super().get_serializer_context()
        context.update({
            'action': self.action,
            'user': self.request.user,
        })
        
        # Add object ID for detail actions
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            context['object_id'] = self.kwargs.get('pk')
        
        # Add parent object ID for nested routes
        for key, value in self.kwargs.items():
            if key.endswith('_pk'):
                context[key] = value
        
        return context
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get statistics for the current queryset.
        
        Returns counts, aggregates, and breakdowns.
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            # Basic counts
            total_count = queryset.count()
            
            stats = {
                'total_count': total_count,
                'generated_at': timezone.now().isoformat(),
            }
            
            # Add status breakdown if model has status field
            if hasattr(queryset.model, 'status'):
                stats['status_breakdown'] = self._get_status_breakdown(queryset)
            
            # Add amount summary if model has amount fields
            if hasattr(queryset.model, 'amount_usd'):
                stats['amount_summary'] = self._get_amount_summary(queryset)
            
            # Add time-based breakdown
            stats['time_breakdown'] = self._get_time_breakdown(queryset)
            
            return Response(stats)
            
        except Exception as e:
            logger.error(f"Stats generation failed: {e}")
            return Response(
                {'error': f'Stats generation failed: {e}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def health(self, request):
        """
        Health check for the ViewSet and related services.
        
        Returns service status and basic metrics.
        """
        try:
            queryset = self.get_queryset()
            
            # Basic health metrics
            health_data = {
                'service': self.__class__.__name__,
                'status': 'healthy',
                'total_records': queryset.count(),
                'model': queryset.model.__name__,
                'timestamp': timezone.now().isoformat(),
            }
            
            # Check recent activity (last 24 hours)
            if hasattr(queryset.model, 'created_at'):
                recent_count = queryset.filter(
                    created_at__gte=timezone.now() - timedelta(hours=24)
                ).count()
                health_data['recent_activity'] = recent_count
            
            return Response(health_data)
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return Response(
                {
                    'service': self.__class__.__name__,
                    'status': 'unhealthy',
                    'error': str(e),
                    'timestamp': timezone.now().isoformat(),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
    
    def _get_status_breakdown(self, queryset) -> Dict[str, int]:
        """Get status breakdown for statistics."""
        return dict(
            queryset.values('status')
            .annotate(count=Count('id'))
            .values_list('status', 'count')
        )
    
    def _get_amount_summary(self, queryset) -> Dict[str, Any]:
        """Get amount summary for statistics."""
        aggregates = queryset.aggregate(
            total_amount=Sum('amount_usd'),
            average_amount=Avg('amount_usd'),
            count=Count('id')
        )
        
        return {
            'total_amount_usd': float(aggregates['total_amount'] or 0),
            'average_amount_usd': float(aggregates['average_amount'] or 0),
            'transaction_count': aggregates['count'],
        }
    
    def _get_time_breakdown(self, queryset) -> Dict[str, int]:
        """Get time-based breakdown for statistics."""
        if not hasattr(queryset.model, 'created_at'):
            return {}
        
        now = timezone.now()
        
        return {
            'last_24h': queryset.filter(
                created_at__gte=now - timedelta(hours=24)
            ).count(),
            'last_7d': queryset.filter(
                created_at__gte=now - timedelta(days=7)
            ).count(),
            'last_30d': queryset.filter(
                created_at__gte=now - timedelta(days=30)
            ).count(),
        }
    
    def handle_exception(self, exc):
        """
        Enhanced exception handling with logging.
        """
        logger.error(f"ViewSet exception in {self.__class__.__name__}: {exc}", extra={
            'action': getattr(self, 'action', 'unknown'),
            'user_id': getattr(self.request.user, 'id', None) if hasattr(self, 'request') else None,
            'exception_type': type(exc).__name__,
        })
        
        return super().handle_exception(exc)


class ReadOnlyPaymentViewSet(PaymentBaseViewSet):
    """
    Read-only base ViewSet for resources that shouldn't be modified via API.
    
    Provides list, retrieve, and stats actions only.
    """
    
    http_method_names = ['get', 'head', 'options']
    
    def create(self, request, *args, **kwargs):
        """Disable create action."""
        return Response(
            {'error': 'Create operation not allowed'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def update(self, request, *args, **kwargs):
        """Disable update action."""
        return Response(
            {'error': 'Update operation not allowed'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def partial_update(self, request, *args, **kwargs):
        """Disable partial update action."""
        return Response(
            {'error': 'Update operation not allowed'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def destroy(self, request, *args, **kwargs):
        """Disable destroy action."""
        return Response(
            {'error': 'Delete operation not allowed'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


class NestedPaymentViewSet(PaymentBaseViewSet):
    """
    Base ViewSet for nested resources (e.g., /users/{id}/payments/).
    
    Automatically filters queryset by parent object and sets parent on creation.
    """
    
    parent_lookup_field = 'user_pk'  # Override in subclasses
    parent_model_field = 'user'      # Override in subclasses
    
    def get_queryset(self):
        """Filter queryset by parent object from URL."""
        queryset = super().get_queryset()
        
        parent_id = self.kwargs.get(self.parent_lookup_field)
        if parent_id:
            filter_kwargs = {self.parent_model_field + '_id': parent_id}
            queryset = queryset.filter(**filter_kwargs)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set parent object when creating nested resource."""
        parent_id = self.kwargs.get(self.parent_lookup_field)
        if parent_id:
            # Get parent model class
            parent_field = getattr(self.queryset.model, self.parent_model_field)
            parent_model = parent_field.field.related_model
            
            try:
                parent_obj = parent_model.objects.get(id=parent_id)
                serializer.save(**{self.parent_model_field: parent_obj})
            except parent_model.DoesNotExist:
                raise NotFound(f"Parent object not found: {parent_id}")
        else:
            serializer.save()
    
    def get_serializer_context(self):
        """Add parent object ID to serializer context."""
        context = super().get_serializer_context()
        
        parent_id = self.kwargs.get(self.parent_lookup_field)
        if parent_id:
            context[self.parent_lookup_field] = parent_id
        
        return context
