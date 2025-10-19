"""
DRF Views for Trading app.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Portfolio, Order
from .serializers import (
    PortfolioSerializer, OrderSerializer, OrderCreateSerializer, PortfolioStatsSerializer
)


@extend_schema_view(
    list=extend_schema(summary="List portfolios", tags=["trading"]),
    retrieve=extend_schema(summary="Get portfolio", tags=["trading"]),
)
class PortfolioViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for trading portfolios."""

    queryset = Portfolio.objects.select_related('user')
    serializer_class = PortfolioSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(summary="Get portfolio statistics", responses={200: PortfolioStatsSerializer}, tags=["trading"])
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get portfolio statistics."""
        stats = {
            'total_portfolios': Portfolio.objects.count(),
            'total_volume_usd': Portfolio.objects.aggregate(total=Sum('total_balance_usd'))['total'] or 0,
            'total_orders': Order.objects.count(),
        }
        serializer = PortfolioStatsSerializer(stats)
        return Response(serializer.data)

    @extend_schema(summary="Get my portfolio", responses={200: PortfolioSerializer}, tags=["trading"])
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's portfolio."""
        portfolio, created = Portfolio.objects.get_or_create(user=request.user)
        serializer = PortfolioSerializer(portfolio)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(summary="List orders", tags=["trading"]),
    retrieve=extend_schema(summary="Get order", tags=["trading"]),
    create=extend_schema(summary="Create order", tags=["trading"]),
)
class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for trading orders."""

    queryset = Order.objects.select_related('portfolio__user')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by current user's portfolio
        if not self.request.user.is_staff:
            queryset = queryset.filter(portfolio__user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        """Create order for current user's portfolio."""
        portfolio, _ = Portfolio.objects.get_or_create(user=self.request.user)
        serializer.save(portfolio=portfolio)
