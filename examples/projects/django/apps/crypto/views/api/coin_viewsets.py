"""
Views for Coin model.
"""

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models
from django.db.models import Sum
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.crypto.models import Coin
from apps.crypto.views.serializers import CoinSerializer, CoinListSerializer, CoinStatsSerializer


@extend_schema_view(
    list=extend_schema(summary="List coins", tags=["crypto"]),
    retrieve=extend_schema(summary="Get coin details", tags=["crypto"]),
)
class CoinViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for cryptocurrency coins."""

    queryset = Coin.objects.filter(is_active=True)
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == 'list':
            return CoinListSerializer
        return CoinSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by tradeable
        tradeable = self.request.query_params.get('tradeable')
        if tradeable:
            queryset = queryset.filter(is_tradeable=True)

        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(symbol__icontains=search) | models.Q(name__icontains=search)
            )

        return queryset.order_by('rank')

    @extend_schema(
        summary="Get coin statistics",
        responses={200: CoinStatsSerializer},
        tags=["crypto"]
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get cryptocurrency statistics."""
        stats = {
            'total_coins': Coin.objects.filter(is_active=True).count(),
            'total_market_cap_usd': Coin.objects.filter(is_active=True).aggregate(
                total=Sum('market_cap_usd')
            )['total'] or 0,
            'total_volume_24h_usd': Coin.objects.filter(is_active=True).aggregate(
                total=Sum('volume_24h_usd')
            )['total'] or 0,
            'trending_coins': Coin.objects.filter(is_active=True).order_by('-volume_24h_usd')[:10]
        }
        serializer = CoinStatsSerializer(stats)
        return Response(serializer.data)
