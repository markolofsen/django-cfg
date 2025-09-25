"""
Currency serializers.
"""

from rest_framework import serializers
from ..models import Currency, Network, ProviderCurrency


class CurrencySerializer(serializers.ModelSerializer):
    """Currency with type info."""
    
    currency_type_display = serializers.CharField(source='get_currency_type_display', read_only=True)
    is_crypto = serializers.SerializerMethodField()
    is_fiat = serializers.SerializerMethodField()
    
    class Meta:
        model = Currency
        fields = [
            'id', 'code', 'name', 'currency_type', 'currency_type_display',
            'is_crypto', 'is_fiat', 'usd_rate', 'rate_updated_at'
        ]
        read_only_fields = ['rate_updated_at']
    
    def get_is_crypto(self, obj):
        """Check if currency is crypto."""
        return obj.is_crypto
    
    def get_is_fiat(self, obj):
        """Check if currency is fiat."""
        return obj.is_fiat


class NetworkSerializer(serializers.ModelSerializer):
    """Network information."""
    
    class Meta:
        model = Network
        fields = ['id', 'code', 'name']


class ProviderCurrencySerializer(serializers.ModelSerializer):
    """Provider currency with base currency and network info."""
    
    base_currency = CurrencySerializer(read_only=True)
    network = NetworkSerializer(read_only=True)
    
    class Meta:
        model = ProviderCurrency
        fields = [
            'id', 'provider_name', 'provider_currency_code', 'base_currency', 'network',
            'is_enabled', 'available_for_payment', 'available_for_payout', 
            'is_popular', 'is_stable', 'min_amount', 'max_amount', 'logo_url'
        ]


class CurrencyListSerializer(serializers.ModelSerializer):
    """Simplified currency for lists."""
    
    currency_type_display = serializers.CharField(source='get_currency_type_display', read_only=True)
    
    class Meta:
        model = Currency
        fields = ['id', 'code', 'name', 'currency_type', 'currency_type_display']
