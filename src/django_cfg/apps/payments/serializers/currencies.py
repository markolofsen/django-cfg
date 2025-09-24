"""
Currency serializers.
"""

from rest_framework import serializers
from ..models import Currency, CurrencyNetwork


class CurrencySerializer(serializers.ModelSerializer):
    """Currency with type info."""
    
    currency_type_display = serializers.CharField(source='get_currency_type_display', read_only=True)
    is_crypto = serializers.SerializerMethodField()
    is_fiat = serializers.SerializerMethodField()
    
    class Meta:
        model = Currency
        fields = [
            'id', 'code', 'name', 'symbol', 'currency_type', 'currency_type_display',
            'is_crypto', 'is_fiat', 'decimal_places', 'usd_rate', 'rate_updated_at',
            'is_active', 'min_payment_amount'
        ]
        read_only_fields = ['rate_updated_at']
    
    def get_is_crypto(self, obj):
        """Check if currency is crypto."""
        return obj.is_crypto
    
    def get_is_fiat(self, obj):
        """Check if currency is fiat."""
        return obj.is_fiat


class CurrencyNetworkSerializer(serializers.ModelSerializer):
    """Currency network with status."""
    
    currency_code = serializers.CharField(source='currency.code', read_only=True)
    currency_name = serializers.CharField(source='currency.name', read_only=True)
    
    class Meta:
        model = CurrencyNetwork
        fields = [
            'id', 'currency', 'currency_code', 'currency_name', 'network_code',
            'network_name', 'is_active', 'confirmation_blocks'
        ]


class CurrencyListSerializer(serializers.ModelSerializer):
    """Simplified currency for lists."""
    
    currency_type_display = serializers.CharField(source='get_currency_type_display', read_only=True)
    
    class Meta:
        model = Currency
        fields = ['id', 'code', 'name', 'currency_type', 'currency_type_display', 'is_active']
