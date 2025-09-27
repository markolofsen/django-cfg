"""
Payment Serializers for Admin Interface.

DRF serializers for payment management in admin dashboard.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from ...models import UniversalPayment

User = get_user_model()


class AdminUserSerializer(serializers.ModelSerializer):
    """
    Simplified user serializer for admin interface.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active']
        read_only_fields = fields


class AdminPaymentListSerializer(serializers.ModelSerializer):
    """
    Serializer for payment list in admin interface.
    """
    user = AdminUserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    provider_display = serializers.CharField(source='get_provider_display', read_only=True)
    age = serializers.SerializerMethodField()
    
    class Meta:
        model = UniversalPayment
        fields = [
            'id', 'user', 'amount_usd', 'currency_code', 'provider', 'provider_display',
            'status', 'status_display', 'pay_amount', 'pay_address', 'transaction_hash',
            'created_at', 'updated_at', 'age', 'description'
        ]
        read_only_fields = fields
    
    def get_age(self, obj):
        """Get human-readable age of payment."""
        return obj.age_display


class AdminPaymentDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for individual payment in admin interface.
    """
    user = AdminUserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    provider_display = serializers.CharField(source='get_provider_display', read_only=True)
    age = serializers.SerializerMethodField()
    
    class Meta:
        model = UniversalPayment
        fields = [
            'id', 'user', 'internal_payment_id', 'amount_usd', 'actual_amount_usd',
            'fee_amount_usd', 'currency_code', 'provider', 'provider_display',
            'status', 'status_display', 'pay_amount', 'pay_address', 'payment_url',
            'transaction_hash', 'confirmations_count', 'security_nonce',
            'expires_at', 'completed_at', 'description', 'callback_url', 'cancel_url',
            'provider_data', 'webhook_data', 'created_at', 'updated_at', 'age'
        ]
        read_only_fields = fields
    
    def get_age(self, obj):
        """Get human-readable age of payment."""
        return obj.age_display


class AdminPaymentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating payments in admin interface.
    """
    class Meta:
        model = UniversalPayment
        fields = [
            'user', 'amount_usd', 'currency_code', 'provider',
            'description', 'callback_url', 'cancel_url'
        ]
    
    def validate_amount_usd(self, value):
        """Validate USD amount."""
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        if value > 100000:  # Max $100k per payment
            raise serializers.ValidationError("Amount exceeds maximum limit")
        return value


class AdminPaymentUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating payments in admin interface.
    """
    class Meta:
        model = UniversalPayment
        fields = [
            'status', 'description', 'callback_url', 'cancel_url',
            'provider_data', 'webhook_data'
        ]
    
    def validate_status(self, value):
        """Validate status transitions."""
        if self.instance and self.instance.status == UniversalPayment.PaymentStatus.COMPLETED:
            if value != UniversalPayment.PaymentStatus.COMPLETED:
                raise serializers.ValidationError("Cannot change status of completed payment")
        return value


class AdminPaymentStatsSerializer(serializers.Serializer):
    """
    Serializer for payment statistics in admin interface.
    """
    total_payments = serializers.IntegerField()
    total_amount_usd = serializers.FloatField()
    successful_payments = serializers.IntegerField()
    failed_payments = serializers.IntegerField()
    pending_payments = serializers.IntegerField()
    success_rate = serializers.FloatField()
    
    # Provider breakdown
    by_provider = serializers.DictField(
        child=serializers.DictField(),
        help_text="Statistics by provider"
    )
    
    # Currency breakdown
    by_currency = serializers.DictField(
        child=serializers.DictField(),
        help_text="Statistics by currency"
    )
    
    # Time-based stats
    last_24h = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="Payments in last 24 hours"
    )
    
    last_7d = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="Payments in last 7 days"
    )
    
    last_30d = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="Payments in last 30 days"
    )
