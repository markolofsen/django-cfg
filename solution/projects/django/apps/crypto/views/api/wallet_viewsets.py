"""
Views for Wallet model.
"""

from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.crypto.models import Wallet
from apps.crypto.views.serializers import WalletSerializer


@extend_schema_view(
    list=extend_schema(summary="List wallets", tags=["crypto"]),
    retrieve=extend_schema(summary="Get wallet details", tags=["crypto"]),
)
class WalletViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for user wallets."""

    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only show current user's wallets
        return Wallet.objects.filter(user=self.request.user).select_related('coin')
