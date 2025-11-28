"""
Serializers for Coin model.
"""

from rest_framework import serializers
from apps.crypto.models import Coin


class CoinSerializer(serializers.ModelSerializer):
    """Serializer for coins."""

    is_price_up_24h = serializers.BooleanField(read_only=True)

    class Meta:
        model = Coin
        fields = [
            'id', 'symbol', 'name', 'slug', 'current_price_usd', 'market_cap_usd',
            'volume_24h_usd', 'price_change_24h_percent', 'price_change_7d_percent',
            'price_change_30d_percent', 'logo_url', 'description', 'website',
            'whitepaper_url', 'rank', 'is_active', 'is_tradeable', 'is_price_up_24h',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CoinListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for coin lists."""

    is_price_up_24h = serializers.BooleanField(read_only=True)

    class Meta:
        model = Coin
        fields = [
            'id', 'symbol', 'name', 'slug', 'current_price_usd', 'market_cap_usd',
            'price_change_24h_percent', 'logo_url', 'rank', 'is_price_up_24h'
        ]


class CoinStatsSerializer(serializers.Serializer):
    """Serializer for coin statistics."""

    total_coins = serializers.IntegerField()
    total_market_cap_usd = serializers.DecimalField(max_digits=20, decimal_places=2)
    total_volume_24h_usd = serializers.DecimalField(max_digits=20, decimal_places=2)
    trending_coins = CoinListSerializer(many=True)
