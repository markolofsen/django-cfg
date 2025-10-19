"""
DRF Serializers for Payments v2.0.

API layer validation (separate from Pydantic service layer).
"""

from decimal import Decimal
from rest_framework import serializers

from ..models import Payment, Transaction, UserBalance, Currency


# Currency Serializers

class CurrencySerializer(serializers.ModelSerializer):
    """Currency list serializer."""

    display_name = serializers.CharField(source='__str__', read_only=True)

    class Meta:
        model = Currency
        fields = [
            'code',
            'name',
            'token',
            'network',
            'display_name',
            'symbol',
            'decimal_places',
            'is_active',
            'min_amount_usd',
            'sort_order',
        ]
        read_only_fields = fields


# Payment Serializers

class PaymentCreateSerializer(serializers.Serializer):
    """Serializer for creating payment."""

    amount_usd = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('1.0'),
        max_value=Decimal('50000.0'),
        help_text="Payment amount in USD"
    )
    currency_code = serializers.CharField(
        max_length=20,
        help_text="Currency code (e.g., USDTTRC20)"
    )
    description = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        help_text="Optional payment description"
    )

    def validate_currency_code(self, value):
        """Validate currency exists and is active."""
        value = value.upper()
        if not Currency.objects.filter(code=value, is_active=True).exists():
            raise serializers.ValidationError(
                f"Currency {value} is not available"
            )
        return value


class PaymentDetailSerializer(serializers.ModelSerializer):
    """Detailed payment information."""

    currency_code = serializers.CharField(source='currency.code', read_only=True)
    currency_name = serializers.CharField(source='currency.name', read_only=True)
    currency_token = serializers.CharField(source='currency.token', read_only=True)
    currency_network = serializers.CharField(source='currency.network', read_only=True)
    qr_code_url = serializers.SerializerMethodField()
    explorer_link = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_completed = serializers.BooleanField(read_only=True)
    is_failed = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id',
            'internal_payment_id',
            'amount_usd',
            'currency_code',
            'currency_name',
            'currency_token',
            'currency_network',
            'pay_amount',
            'actual_amount',
            'actual_amount_usd',
            'status',
            'status_display',
            'pay_address',
            'qr_code_url',
            'payment_url',
            'transaction_hash',
            'explorer_link',
            'confirmations_count',
            'expires_at',
            'completed_at',
            'created_at',
            'is_completed',
            'is_failed',
            'is_expired',
            'description',
        ]
        read_only_fields = fields

    def get_qr_code_url(self, obj) -> str | None:
        """Get QR code URL."""
        return obj.get_qr_code_url() if obj.pay_address else None

    def get_explorer_link(self, obj) -> str | None:
        """Get blockchain explorer link."""
        return obj.get_explorer_link() if obj.transaction_hash else None


class PaymentListSerializer(serializers.ModelSerializer):
    """Payment list item (lighter than detail)."""

    currency_code = serializers.CharField(source='currency.code', read_only=True)
    currency_token = serializers.CharField(source='currency.token', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id',
            'internal_payment_id',
            'amount_usd',
            'currency_code',
            'currency_token',
            'status',
            'status_display',
            'created_at',
            'completed_at',
        ]
        read_only_fields = fields


class PaymentStatusSerializer(serializers.Serializer):
    """Payment status response."""

    status = serializers.CharField(read_only=True)
    is_completed = serializers.BooleanField(read_only=True)
    transaction_hash = serializers.CharField(read_only=True, allow_null=True)
    message = serializers.CharField(read_only=True, allow_null=True)


# Balance Serializers

class BalanceSerializer(serializers.ModelSerializer):
    """User balance serializer."""

    balance_display = serializers.CharField(read_only=True)

    class Meta:
        model = UserBalance
        fields = [
            'balance_usd',
            'balance_display',
            'total_deposited',
            'total_withdrawn',
            'last_transaction_at',
        ]
        read_only_fields = fields


class TransactionSerializer(serializers.ModelSerializer):
    """Transaction serializer."""

    type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    amount_display = serializers.CharField(read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id',
            'transaction_type',
            'type_display',
            'amount_usd',
            'amount_display',
            'balance_after',
            'payment_id',
            'description',
            'created_at',
        ]
        read_only_fields = fields


# Response Serializers (for standardized API responses)

class SuccessResponseSerializer(serializers.Serializer):
    """Standard success response."""

    success = serializers.BooleanField(default=True)
    message = serializers.CharField(required=False)
    data = serializers.DictField(required=False)


class ErrorResponseSerializer(serializers.Serializer):
    """Standard error response."""

    success = serializers.BooleanField(default=False)
    error = serializers.CharField()
    errors = serializers.DictField(required=False)


# Pagination Serializers

class PaginatedResponseSerializer(serializers.Serializer):
    """Paginated response wrapper."""

    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)
    results = serializers.ListField()
