"""
Base ViewSet classes for Admin Interface API.

Common functionality for all admin interface ViewSets.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from datetime import timedelta


from django_cfg.modules.django_logger import get_logger

logger = get_logger("admin_api")


class AdminBaseViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet for admin interface with staff permissions.
    
    Provides standard CRUD operations with admin-only access.
    """
    
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering = ['-created_at']
    
    # Serializer classes mapping for different actions
    serializer_classes = {}
    
    def get_queryset(self):
        """
        Optimized queryset for admin interface.
        
        Override in subclasses to add specific optimizations.
        """
        queryset = super().get_queryset()
        
        # Add common optimizations for admin
        if hasattr(self.queryset.model, 'user'):
            queryset = queryset.select_related('user')
        
        return queryset
    
    def get_serializer_class(self):
        """
        Dynamic serializer selection based on action.
        """
        serializer_classes = getattr(self, 'serializer_classes', {})
        return serializer_classes.get(self.action, self.serializer_class)
    
    def get_serializer_context(self):
        """Enhanced context for admin serializers."""
        context = super().get_serializer_context()
        context.update({
            'is_admin': True,
            'admin_user': self.request.user,
        })
        return context
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get statistics for this resource."""
        queryset = self.get_queryset()
        stats = {
            'total': queryset.count(),
            'recent': queryset.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            ).count(),
        }
        return Response(stats)


class AdminReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for admin interface.
    
    For resources that should only be viewed, not modified.
    """
    
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering = ['-created_at']
    
    def get_serializer_context(self):
        """Enhanced context for admin serializers."""
        context = super().get_serializer_context()
        context.update({
            'is_admin': True,
            'admin_user': self.request.user,
        })
        return context


class AdminTemplateViewMixin:
    """
    Mixin for template views requiring staff access.
    """
    
    def get_context_data(self, **kwargs):
        """Add admin-specific context."""
        context = super().get_context_data(**kwargs)
        context.update({
            'is_admin_interface': True,
            'admin_user': self.request.user,
        })
        return context
