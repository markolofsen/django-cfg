"""DRF Views for Crypto app."""

from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.crypto.models import CoinListing
from apps.crypto.api.serializers import (
    CoinListingSerializer,
    CoinListingWriteSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="List coin listings",
        description="Get a paginated list of all coin listings ordered by market cap.",
        tags=["Crypto"],
    ),
    create=extend_schema(
        summary="Create coin listing",
        description="Create a new coin listing.",
        tags=["Crypto"],
    ),
    retrieve=extend_schema(
        summary="Get coin listing",
        description="Get detailed information about a specific coin listing.",
        tags=["Crypto"],
    ),
    update=extend_schema(
        summary="Update coin listing",
        description="Update coin listing fields.",
        tags=["Crypto"],
    ),
    partial_update=extend_schema(
        summary="Partially update coin listing",
        description="Partially update coin listing fields.",
        tags=["Crypto"],
    ),
    destroy=extend_schema(
        summary="Delete coin listing",
        description="Delete a coin listing.",
        tags=["Crypto"],
    ),
)
class CoinListingViewSet(viewsets.ModelViewSet):
    """ViewSet for managing coin listings."""

    queryset = CoinListing.objects.all()
    serializer_class = CoinListingSerializer
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return CoinListingWriteSerializer
        return CoinListingSerializer
