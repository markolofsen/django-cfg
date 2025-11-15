"""
Serializers for Wallet model.
"""

from rest_framework import serializers
from apps.crypto.models import Wallet
from .coin_serializers import CoinListSerializer


class WalletSerializer(serializers.ModelSerializer):
    """Serializer for wallets."""

    coin_info = CoinListSerializer(source='coin', read_only=True)
    total_balance = serializers.DecimalField(max_digits=20, decimal_places=8, read_only=True)
    value_usd = serializers.DecimalField(max_digits=20, decimal_places=8, read_only=True)

    class Meta:
        model = Wallet
        fields = [
            'id', 'user', 'coin', 'coin_info', 'balance', 'locked_balance',
            'total_balance', 'value_usd', 'address', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'locked_balance', 'created_at', 'updated_at']
