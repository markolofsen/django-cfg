"""
Admin User ViewSet.

Simple ViewSet for user management in admin interface.
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from django_cfg.apps.payments.admin_interface.views.base import AdminReadOnlyViewSet
from django_cfg.apps.payments.admin_interface.serializers import AdminUserSerializer
from django_cfg.modules.django_logger import get_logger

logger = get_logger("admin_user_api")

User = get_user_model()


class AdminUserViewSet(AdminReadOnlyViewSet):
    """
    Admin ViewSet for user management.
    
    Provides read-only access to users for admin interface.
    """
    
    queryset = User.objects.filter(is_active=True).order_by('username')
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUser]
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'email', 'date_joined']
    ordering = ['username']  # Override base class ordering
    
    def get_queryset(self):
        """Optimized queryset for admin interface."""
        # Don't slice here - let DRF handle pagination and ordering first
        return super().get_queryset()
    
    def list(self, request, *args, **kwargs):
        """Override list to limit results for dropdown."""
        # Get the filtered and ordered queryset from DRF
        queryset = self.filter_queryset(self.get_queryset())
        
        # Now apply limit after filtering/ordering
        queryset = queryset[:100]  # Limit to first 100 users
        
        # Use DRF pagination if needed
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
