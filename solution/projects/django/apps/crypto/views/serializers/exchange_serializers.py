"""
Serializers for Exchange model.
"""

from rest_framework import serializers
from apps.crypto.models import Exchange


class ExchangeSerializer(serializers.ModelSerializer):
    """Serializer for exchanges."""

    class Meta:
        model = Exchange
        fields = [
            'id', 'name', 'slug', 'code', 'description', 'website', 'logo_url',
            'volume_24h_usd', 'num_markets', 'num_coins', 'maker_fee_percent',
            'taker_fee_percent', 'is_active', 'is_verified', 'supports_api',
            'rank', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
