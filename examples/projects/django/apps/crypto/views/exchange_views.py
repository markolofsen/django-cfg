"""
Views for Exchange model.
"""

from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.crypto.models import Exchange
from apps.crypto.serializers import ExchangeSerializer


@extend_schema_view(
    list=extend_schema(summary="List exchanges", tags=["crypto"]),
    retrieve=extend_schema(summary="Get exchange details", tags=["crypto"]),
)
class ExchangeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for cryptocurrency exchanges."""

    queryset = Exchange.objects.filter(is_active=True).order_by('rank')
    serializer_class = ExchangeSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
