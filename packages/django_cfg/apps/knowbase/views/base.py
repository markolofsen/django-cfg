"""
Base views for knowledge base API.
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from typing import Type, Any
import logging

logger = logging.getLogger(__name__)


class BaseKnowledgeViewSet(viewsets.ModelViewSet):
    """Base ViewSet with common knowledge base functionality."""
    
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    
    def get_queryset(self):
        """Filter queryset by authenticated user."""
        if hasattr(self, 'queryset') and self.queryset is not None:
            return self.queryset.filter(user=self.request.user)
        return super().get_queryset()
    
    def perform_create(self, serializer):
        """Automatically set user on creation."""
        serializer.save(user=self.request.user)
    
    def handle_exception(self, exc):
        """Enhanced error handling with logging."""
        logger.error(
            f"API Error in {self.__class__.__name__}: {exc}",
            extra={
                'user_id': getattr(self.request.user, 'id', None),
                'path': self.request.path,
                'method': self.request.method,
                'data': getattr(self.request, 'data', None)
            }
        )
        return super().handle_exception(exc)
    
    def get_service(self):
        """Get service instance for this view."""
        if not hasattr(self, 'service_class'):
            raise NotImplementedError("ViewSet must define service_class")
        return self.service_class(user=self.request.user)