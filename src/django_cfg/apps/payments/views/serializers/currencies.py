"""
Currency serializers for the Universal Payment System v2.0.

DRF serializers for currency operations with service integration.
"""

from rest_framework import serializers
from typing import Dict, Any

from ...models import Currency, Network, ProviderCurrency
from ...services import get_currency_service
from django_cfg.modules.django_logger import get_logger

logger = get_logger("currency_serializers")


class CurrencySerializer(serializers.ModelSerializer):
    """
    Complete currency serializer with full details.
    
    Used for currency information and management.
    """
    
    type_display = serializers.CharField(source='get_currency_type_display', read_only=True)
    
    class Meta:
        model = Currency
        fields = [
            'id',
            'code',
            'name',
            'symbol',
            'currency_type',
            'type_display',
            'decimal_places',
            'is_active',
            'is_crypto',
            'is_fiat',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class CurrencyListSerializer(serializers.ModelSerializer):
    """
    Lightweight currency serializer for lists.
    
    Optimized for currency selection and lists.
    """
    
    type_display = serializers.CharField(source='get_currency_type_display', read_only=True)
    
    class Meta:
        model = Currency
        fields = [
            'id',
            'code',
            'name',
            'symbol',
            'currency_type',
            'type_display',
            'is_active',
        ]
        read_only_fields = fields


class NetworkSerializer(serializers.ModelSerializer):
    """
    Network serializer for blockchain networks.
    
    Used for network information and selection.
    """
    
    currency = CurrencyListSerializer(read_only=True)
    
    class Meta:
        model = Network
        fields = [
            'id',
            'currency',
            'name',
            'code',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class ProviderCurrencySerializer(serializers.ModelSerializer):
    """
    Provider currency serializer for provider-specific currency info.
    
    Used for provider currency management and rates.
    """
    
    currency = CurrencyListSerializer(read_only=True)
    network = NetworkSerializer(read_only=True)
    
    class Meta:
        model = ProviderCurrency
        fields = [
            'id',
            'currency',
            'network',
            'provider',
            'provider_currency_code',
            'min_amount',
            'max_amount',
            'fee_percentage',
            'is_enabled',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class CurrencyConversionSerializer(serializers.Serializer):
    """
    Currency conversion serializer with service integration.
    
    Handles currency conversion requests through CurrencyService.
    """
    
    from_currency = serializers.CharField(
        max_length=10,
        help_text="Source currency code (e.g., USD, BTC)"
    )
    to_currency = serializers.CharField(
        max_length=10,
        help_text="Target currency code (e.g., USD, BTC)"
    )
    amount = serializers.FloatField(
        min_value=0.01,
        help_text="Amount to convert"
    )
    provider = serializers.ChoiceField(
        choices=[('nowpayments', 'NowPayments')],
        default='nowpayments',
        required=False,
        help_text="Provider for conversion rates"
    )
    
    def validate_from_currency(self, value: str) -> str:
        """Validate source currency exists."""
        if not Currency.objects.filter(code=value.upper(), is_active=True).exists():
            raise serializers.ValidationError(f"Currency {value} not found or inactive")
        return value.upper()
    
    def validate_to_currency(self, value: str) -> str:
        """Validate target currency exists."""
        if not Currency.objects.filter(code=value.upper(), is_active=True).exists():
            raise serializers.ValidationError(f"Currency {value} not found or inactive")
        return value.upper()
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate conversion request."""
        if attrs['from_currency'] == attrs['to_currency']:
            raise serializers.ValidationError("Source and target currencies cannot be the same")
        
        return attrs
    
    def save(self) -> Dict[str, Any]:
        """Perform currency conversion using CurrencyService."""
        try:
            currency_service = get_currency_service()
            result = currency_service.convert_currency(
                from_currency=self.validated_data['from_currency'],
                to_currency=self.validated_data['to_currency'],
                amount=self.validated_data['amount'],
                provider=self.validated_data.get('provider', 'nowpayments')
            )
            
            if result.success:
                return {
                    'success': True,
                    'conversion': result.data,
                    'message': result.message
                }
            else:
                return {
                    'success': False,
                    'error': result.message,
                    'error_code': result.error_code
                }
                
        except Exception as e:
            logger.error(f"Currency conversion error: {e}")
            return {
                'success': False,
                'error': f"Conversion failed: {e}",
                'error_code': 'conversion_error'
            }


class CurrencyRatesSerializer(serializers.Serializer):
    """
    Currency rates serializer for getting exchange rates.
    
    Fetches current exchange rates through CurrencyService.
    """
    
    base_currency = serializers.CharField(
        default='USD',
        max_length=10,
        help_text="Base currency for rates (default: USD)"
    )
    currencies = serializers.ListField(
        child=serializers.CharField(max_length=10),
        required=False,
        help_text="Specific currencies to get rates for (optional)"
    )
    provider = serializers.ChoiceField(
        choices=[('nowpayments', 'NowPayments')],
        default='nowpayments',
        required=False,
        help_text="Provider for exchange rates"
    )
    
    def validate_base_currency(self, value: str) -> str:
        """Validate base currency exists."""
        if not Currency.objects.filter(code=value.upper(), is_active=True).exists():
            raise serializers.ValidationError(f"Base currency {value} not found or inactive")
        return value.upper()
    
    def validate_currencies(self, value: list) -> list:
        """Validate requested currencies exist."""
        if value:
            upper_currencies = [c.upper() for c in value]
            existing_currencies = set(
                Currency.objects.filter(
                    code__in=upper_currencies,
                    is_active=True
                ).values_list('code', flat=True)
            )
            
            missing_currencies = set(upper_currencies) - existing_currencies
            if missing_currencies:
                raise serializers.ValidationError(
                    f"Currencies not found or inactive: {', '.join(missing_currencies)}"
                )
            
            return upper_currencies
        return value
    
    def save(self) -> Dict[str, Any]:
        """Get currency rates using CurrencyService."""
        try:
            currency_service = get_currency_service()
            result = currency_service.get_exchange_rates(
                base_currency=self.validated_data['base_currency'],
                currencies=self.validated_data.get('currencies'),
                provider=self.validated_data.get('provider', 'nowpayments')
            )
            
            if result.success:
                return {
                    'success': True,
                    'rates': result.data,
                    'message': result.message
                }
            else:
                return {
                    'success': False,
                    'error': result.message,
                    'error_code': result.error_code
                }
                
        except Exception as e:
            logger.error(f"Currency rates error: {e}")
            return {
                'success': False,
                'error': f"Rates fetch failed: {e}",
                'error_code': 'rates_error'
            }


class SupportedCurrenciesSerializer(serializers.Serializer):
    """
    Supported currencies serializer for provider capabilities.
    
    Gets supported currencies from providers through CurrencyService.
    """
    
    provider = serializers.ChoiceField(
        choices=[('nowpayments', 'NowPayments')],
        default='nowpayments',
        required=False,
        help_text="Provider to get supported currencies from"
    )
    currency_type = serializers.ChoiceField(
        choices=[
            ('all', 'All'),
            ('crypto', 'Cryptocurrency'),
            ('fiat', 'Fiat Currency'),
        ],
        default='all',
        required=False,
        help_text="Filter by currency type"
    )
    
    def save(self) -> Dict[str, Any]:
        """Get supported currencies using CurrencyService."""
        try:
            currency_service = get_currency_service()
            result = currency_service.get_supported_currencies(
                provider=self.validated_data.get('provider', 'nowpayments'),
                currency_type=self.validated_data.get('currency_type', 'all')
            )
            
            if result.success:
                return {
                    'success': True,
                    'currencies': result.data,
                    'message': result.message
                }
            else:
                return {
                    'success': False,
                    'error': result.message,
                    'error_code': result.error_code
                }
                
        except Exception as e:
            logger.error(f"Supported currencies error: {e}")
            return {
                'success': False,
                'error': f"Supported currencies fetch failed: {e}",
                'error_code': 'supported_currencies_error'
            }
