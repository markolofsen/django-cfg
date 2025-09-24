"""
Payment serializers.
"""

from rest_framework import serializers
from ..models import UniversalPayment


class UniversalPaymentSerializer(serializers.ModelSerializer):
    """Universal payment with status info."""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    provider_display = serializers.CharField(source='get_provider_display', read_only=True)
    is_pending = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()
    is_failed = serializers.ReadOnlyField()
    
    class Meta:
        model = UniversalPayment
        fields = [
            'id', 'internal_payment_id', 'provider_payment_id', 'order_id',
            'amount_usd', 'currency_code', 'actual_amount_usd', 'actual_currency_code',
            'fee_amount_usd', 'provider', 'provider_display', 'status', 'status_display',
            'pay_address', 'pay_amount', 'network', 'description',
            'is_pending', 'is_completed', 'is_failed',
            'expires_at', 'completed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'internal_payment_id', 'provider_payment_id', 
            'actual_amount_usd', 'actual_currency_code', 'fee_amount_usd',
            'pay_address', 'pay_amount', 'completed_at', 'processed_at',
            'created_at', 'updated_at'
        ]


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Create payment request."""
    
    class Meta:
        model = UniversalPayment
        fields = [
            'amount_usd', 'currency_code', 'provider', 'description', 'order_id'
        ]
    
    def validate_amount_usd(self, value):
        """Validate payment amount."""
        if value < 1.0:
            raise serializers.ValidationError("Minimum payment amount is $1.00")
        return value


class PaymentListSerializer(serializers.ModelSerializer):
    """Simplified payment for lists."""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = UniversalPayment
        fields = [
            'id', 'internal_payment_id', 'amount_usd', 'currency_code',
            'provider', 'status', 'status_display', 'description', 'created_at'
        ]
