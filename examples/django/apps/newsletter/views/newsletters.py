"""
Newsletter views.
"""

from rest_framework import generics
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema

from ..models import Newsletter
from ..serializers import NewsletterSerializer


class NewsletterListView(generics.ListAPIView):
    """List all active newsletters."""
    
    queryset = Newsletter.objects.filter(is_active=True)
    serializer_class = NewsletterSerializer
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="List Active Newsletters",
        description="Get a list of all active newsletters available for subscription.",
        responses={200: NewsletterSerializer(many=True)},
        tags=["Newsletters"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class NewsletterDetailView(generics.RetrieveAPIView):
    """Retrieve a specific newsletter."""
    
    queryset = Newsletter.objects.filter(is_active=True)
    serializer_class = NewsletterSerializer
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Get Newsletter Details",
        description="Retrieve details of a specific newsletter.",
        responses={200: NewsletterSerializer},
        tags=["Newsletters"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
