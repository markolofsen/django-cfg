"""
Payment Serializers for Admin Interface.

DRF serializers for payment management in admin dashboard.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.humanize.templatetags.humanize import naturaltime

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


class AdminPaymentListSerializer(serializers.Serializer):
    """
    Serializer for payment list in admin interface.
    Uses UniversalPayment only for data extraction.
    """
    id = serializers.UUIDField(read_only=True)
    user = AdminUserSerializer(read_only=True)
    amount_usd = serializers.FloatField(read_only=True)
    currency_code = serializers.SerializerMethodField()
    currency_name = serializers.SerializerMethodField()
    provider = serializers.CharField(read_only=True)
    provider_display = serializers.SerializerMethodField()
    status = serializers.CharField(read_only=True)
    status_display = serializers.SerializerMethodField()
    pay_amount = serializers.DecimalField(max_digits=20, decimal_places=8, read_only=True)
    pay_address = serializers.CharField(read_only=True)
    transaction_hash = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    description = serializers.CharField(read_only=True)
    age = serializers.SerializerMethodField()
    
    def get_currency_code(self, obj):
        """Get currency code from related Currency model."""
        return obj.currency.code if obj.currency else None
    
    def get_currency_name(self, obj):
        """Get currency name from related Currency model."""
        return obj.currency.name if obj.currency else None
    
    def get_provider_display(self, obj):
        """Get human-readable provider name."""
        return obj.get_provider_display()
    
    def get_status_display(self, obj):
        """Get human-readable status."""
        return obj.get_status_display()
    
    def get_age(self, obj):
        """Get human-readable age of payment."""
        from django.contrib.humanize.templatetags.humanize import naturaltime
        return naturaltime(obj.created_at)


class AdminPaymentDetailSerializer(serializers.Serializer):
    """
    Detailed serializer for individual payment in admin interface.
    Uses UniversalPayment only for data extraction.
    """
    id = serializers.UUIDField(read_only=True)
    user = AdminUserSerializer(read_only=True)
    internal_payment_id = serializers.CharField(read_only=True)
    amount_usd = serializers.FloatField(read_only=True)
    actual_amount_usd = serializers.FloatField(read_only=True)
    fee_amount_usd = serializers.FloatField(read_only=True)
    currency_code = serializers.SerializerMethodField()
    currency_name = serializers.SerializerMethodField()
    provider = serializers.CharField(read_only=True)
    provider_display = serializers.SerializerMethodField()
    status = serializers.CharField(read_only=True)
    status_display = serializers.SerializerMethodField()
    pay_amount = serializers.DecimalField(max_digits=20, decimal_places=8, read_only=True)
    pay_address = serializers.CharField(read_only=True)
    payment_url = serializers.URLField(read_only=True)
    transaction_hash = serializers.CharField(read_only=True)
    confirmations_count = serializers.IntegerField(read_only=True)
    security_nonce = serializers.CharField(read_only=True)
    expires_at = serializers.DateTimeField(read_only=True)
    completed_at = serializers.DateTimeField(read_only=True)
    status_changed_at = serializers.DateTimeField(read_only=True)
    description = serializers.CharField(read_only=True)
    callback_url = serializers.URLField(read_only=True)
    cancel_url = serializers.URLField(read_only=True)
    provider_data = serializers.JSONField(read_only=True)
    webhook_data = serializers.JSONField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    age = serializers.SerializerMethodField()
    
    def get_currency_code(self, obj):
        """Get currency code from related Currency model."""
        return obj.currency.code if obj.currency else None
    
    def get_currency_name(self, obj):
        """Get currency name from related Currency model."""
        return obj.currency.name if obj.currency else None
    
    def get_provider_display(self, obj):
        """Get human-readable provider name."""
        return obj.get_provider_display()
    
    def get_status_display(self, obj):
        """Get human-readable status."""
        return obj.get_status_display()
    
    def get_age(self, obj):
        """Get human-readable age of payment."""
        return naturaltime(obj.created_at)


class AdminPaymentCreateSerializer(serializers.Serializer):
    """
    Serializer for creating payments in admin interface.
    Uses UniversalPayment only for data creation.
    """
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    amount_usd = serializers.FloatField(min_value=1.0, max_value=100000.0)
    currency_code = serializers.CharField(max_length=20, help_text="Provider currency code (e.g., BTC, ZROERC20)", write_only=True)
    provider = serializers.CharField(max_length=50)
    description = serializers.CharField(required=False, allow_blank=True)
    callback_url = serializers.URLField(required=False, allow_blank=True)
    cancel_url = serializers.URLField(required=False, allow_blank=True)
    
    def validate_amount_usd(self, value):
        """Validate USD amount."""
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        if value > 100000:  # Max $100k per payment
            raise serializers.ValidationError("Amount exceeds maximum limit")
        return value
    
    def create(self, validated_data):
        """Create payment using PaymentService for proper provider integration."""
        from django_cfg.apps.payments.services.core.payment_service import PaymentService
        from django_cfg.apps.payments.services.types.requests import PaymentCreateRequest
        from django_cfg.apps.payments.models import ProviderCurrency
        
        # Extract provider_currency_code and find original currency
        provider_currency_code = validated_data.pop('currency_code')
        
        # Find the ProviderCurrency to get original currency code
        try:
            provider_currency = ProviderCurrency.objects.select_related('currency').get(
                provider_currency_code=provider_currency_code,
                provider=validated_data['provider'],
                is_enabled=True
            )
            original_currency_code = provider_currency.currency.code
        except ProviderCurrency.DoesNotExist:
            raise serializers.ValidationError(f"Provider currency {provider_currency_code} not found for {validated_data['provider']}")
        
        # Create PaymentCreateRequest for the service
        payment_request = PaymentCreateRequest(
            user_id=validated_data['user'].id,
            amount_usd=validated_data['amount_usd'],
            currency_code=original_currency_code,  # Use original currency code
            provider=validated_data['provider'],
            description=validated_data.get('description', ''),
            callback_url=validated_data.get('callback_url', ''),
            cancel_url=validated_data.get('cancel_url', ''),
            metadata={'provider_currency_code': provider_currency_code}  # Store provider code in metadata
        )
        
        # Use PaymentService to create payment with provider integration
        payment_service = PaymentService()
        result = payment_service.create_payment(payment_request)
        
        if result.success:
            # Get the created payment object from database using payment_id
            from django_cfg.apps.payments.models import UniversalPayment
            payment = UniversalPayment.objects.get(id=result.payment_id)
            return payment
        else:
            raise serializers.ValidationError(f"Payment creation failed: {result.message}")
    
    def to_representation(self, instance):
        """Return created payment with ID and currency info."""
        if instance:
            return {
                'id': str(instance.id),
                'user': instance.user.id,
                'amount_usd': instance.amount_usd,
                'currency_code': instance.currency.code if instance.currency else None,
                'currency_name': instance.currency.name if instance.currency else None,
                'provider': instance.provider,
                'description': instance.description,
                'callback_url': instance.callback_url,
                'cancel_url': instance.cancel_url,
                'internal_payment_id': instance.internal_payment_id,
                'status': instance.status,
                'created_at': instance.created_at.isoformat() if instance.created_at else None
            }
        return super().to_representation(instance)


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
