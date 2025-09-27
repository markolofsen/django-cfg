"""
Payment serializers for the Universal Payment System v2.0.

DRF serializers with Pydantic integration and service layer validation.
"""

from rest_framework import serializers
from decimal import Decimal
from typing import Dict, Any
from django.contrib.auth import get_user_model

from ...models import UniversalPayment
from ...services import get_payment_service, PaymentCreateRequest, PaymentStatusRequest
from django_cfg.modules.django_logger import get_logger

User = get_user_model()
logger = get_logger("payment_serializers")


class PaymentListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for payment lists.
    
    Optimized for list views with minimal data.
    """
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    amount_display = serializers.SerializerMethodField(read_only=True)
    
    def get_amount_display(self, obj):
        """Get formatted amount display."""
        return f"${obj.amount_usd:.2f}"
    
    class Meta:
        model = UniversalPayment
        fields = [
            'id',
            'amount_usd',
            'currency',
            'provider',
            'status',
            'status_display',
            'amount_display',
            'created_at',
            'expires_at',
        ]
        read_only_fields = fields


class PaymentSerializer(serializers.ModelSerializer):
    """
    Complete payment serializer with full details.
    
    Used for detail views and updates.
    """
    
    user = serializers.StringRelatedField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    amount_display = serializers.SerializerMethodField(read_only=True)
    
    # Status check methods
    is_pending = serializers.SerializerMethodField(read_only=True)
    is_completed = serializers.SerializerMethodField(read_only=True)
    is_failed = serializers.SerializerMethodField(read_only=True)
    is_expired = serializers.SerializerMethodField(read_only=True)
    
    def get_amount_display(self, obj):
        """Get formatted amount display."""
        return f"${obj.amount_usd:.2f}"
    
    def get_is_pending(self, obj):
        """Check if payment is pending."""
        return obj.status == obj.PaymentStatus.PENDING
    
    def get_is_completed(self, obj):
        """Check if payment is completed."""
        return obj.status == obj.PaymentStatus.COMPLETED
    
    def get_is_failed(self, obj):
        """Check if payment is failed."""
        return obj.status == obj.PaymentStatus.FAILED
    
    def get_is_expired(self, obj):
        """Check if payment is expired."""
        return obj.status == obj.PaymentStatus.EXPIRED
    
    class Meta:
        model = UniversalPayment
        fields = [
            'id',
            'user',
            'amount_usd',
            'currency',
            'network',
            'provider',
            'status',
            'status_display',
            'amount_display',
            'provider_payment_id',
            'payment_url',
            'pay_address',
            'callback_url',
            'cancel_url',
            'description',
            'transaction_hash',
            'confirmations_count',
            'created_at',
            'updated_at',
            'expires_at',
            'completed_at',
            # Status methods
            'is_pending',
            'is_completed',
            'is_failed',
            'is_expired',
        ]
        read_only_fields = [
            'id',
            'user',
            'provider_payment_id',
            'payment_url',
            'pay_address',
            'transaction_hash',
            'confirmations_count',
            'created_at',
            'updated_at',
            'completed_at',
            'status_display',
            'amount_display',
            'is_pending',
            'is_completed',
            'is_failed',
            'is_expired',
        ]


class PaymentCreateSerializer(serializers.Serializer):
    """
    Payment creation serializer with Pydantic integration.
    
    Validates input and delegates to PaymentService.
    """
    
    amount_usd = serializers.FloatField(
        min_value=1.0,
        max_value=50000.0,
        help_text="Amount in USD (1.00 - 50,000.00)"
    )
    currency_code = serializers.ChoiceField(
        choices=[
            ('BTC', 'Bitcoin'),
            ('ETH', 'Ethereum'),
            ('LTC', 'Litecoin'),
            ('XMR', 'Monero'),
            ('USDT', 'Tether'),
            ('USDC', 'USD Coin'),
            ('ADA', 'Cardano'),
            ('DOT', 'Polkadot'),
        ],
        help_text="Cryptocurrency to receive"
    )
    provider = serializers.ChoiceField(
        choices=[('nowpayments', 'NowPayments')],
        default='nowpayments',
        help_text="Payment provider"
    )
    callback_url = serializers.URLField(
        required=False,
        allow_blank=True,
        help_text="Success callback URL"
    )
    cancel_url = serializers.URLField(
        required=False,
        allow_blank=True,
        help_text="Cancellation URL"
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        help_text="Payment description"
    )
    metadata = serializers.JSONField(
        required=False,
        default=dict,
        help_text="Additional metadata"
    )
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate payment creation data."""
        try:
            # Create Pydantic request for validation
            request = PaymentCreateRequest(
                user_id=self.context['request'].user.id,
                **attrs
            )
            
            # Store validated request for create method
            self._validated_request = request
            return attrs
            
        except Exception as e:
            logger.error(f"Payment validation failed: {e}")
            raise serializers.ValidationError(f"Invalid payment data: {e}")
    
    def create(self, validated_data: Dict[str, Any]) -> UniversalPayment:
        """Create payment using PaymentService."""
        try:
            payment_service = get_payment_service()
            
            # Use pre-validated Pydantic request
            result = payment_service.create_payment(self._validated_request)
            
            if result.success:
                # Get the created payment from database
                payment = UniversalPayment.objects.get(id=result.payment_id)
                
                logger.info(f"Payment created successfully", extra={
                    'payment_id': result.payment_id,
                    'user_id': self._validated_request.user_id,
                    'amount_usd': self._validated_request.amount_usd
                })
                
                return payment
            else:
                logger.error(f"Payment creation failed: {result.message}")
                raise serializers.ValidationError(result.message)
                
        except Exception as e:
            logger.error(f"Payment creation error: {e}")
            raise serializers.ValidationError(f"Payment creation failed: {e}")
    
    def to_representation(self, instance: UniversalPayment) -> Dict[str, Any]:
        """Return full payment data after creation."""
        return PaymentSerializer(instance, context=self.context).data


class PaymentStatusSerializer(serializers.Serializer):
    """
    Payment status check serializer.
    
    Used for checking payment status via provider API.
    """
    
    force_provider_check = serializers.BooleanField(
        default=False,
        help_text="Force check with payment provider"
    )
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate status check request."""
        payment_id = self.context.get('payment_id')
        if not payment_id:
            raise serializers.ValidationError("Payment ID is required")
        
        user = self.context['request'].user
        
        # Create Pydantic request
        self._status_request = PaymentStatusRequest(
            payment_id=payment_id,
            user_id=user.id,
            force_provider_check=attrs.get('force_provider_check', False)
        )
        
        return attrs
    
    def save(self) -> Dict[str, Any]:
        """Check payment status using PaymentService."""
        try:
            payment_service = get_payment_service()
            result = payment_service.get_payment_status(self._status_request)
            
            if result.success:
                # Get updated payment from database
                payment = UniversalPayment.objects.get(id=result.payment_id)
                
                return {
                    'success': True,
                    'payment': PaymentSerializer(payment, context=self.context).data,
                    'provider_checked': self._status_request.force_provider_check,
                    'message': result.message
                }
            else:
                return {
                    'success': False,
                    'error': result.message,
                    'error_code': result.error_code
                }
                
        except Exception as e:
            logger.error(f"Payment status check error: {e}")
            return {
                'success': False,
                'error': f"Status check failed: {e}",
                'error_code': 'status_check_error'
            }


class PaymentCancelSerializer(serializers.Serializer):
    """
    Payment cancellation serializer.
    
    Used for cancelling payments.
    """
    
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        help_text="Cancellation reason"
    )
    
    def save(self) -> Dict[str, Any]:
        """Cancel payment using PaymentService."""
        try:
            payment_id = self.context.get('payment_id')
            if not payment_id:
                raise serializers.ValidationError("Payment ID is required")
            
            payment_service = get_payment_service()
            result = payment_service.cancel_payment(
                payment_id=payment_id,
                reason=self.validated_data.get('reason')
            )
            
            if result.success:
                # Get updated payment
                payment = UniversalPayment.objects.get(id=result.payment_id)
                
                return {
                    'success': True,
                    'payment': PaymentSerializer(payment, context=self.context).data,
                    'message': result.message
                }
            else:
                return {
                    'success': False,
                    'error': result.message,
                    'error_code': result.error_code
                }
                
        except Exception as e:
            logger.error(f"Payment cancellation error: {e}")
            return {
                'success': False,
                'error': f"Cancellation failed: {e}",
                'error_code': 'cancellation_error'
            }


class PaymentStatsSerializer(serializers.Serializer):
    """
    Payment statistics serializer.
    
    Used for payment analytics and reporting.
    """
    
    days = serializers.IntegerField(
        default=30,
        min_value=1,
        max_value=365,
        help_text="Number of days to analyze"
    )
    
    def save(self) -> Dict[str, Any]:
        """Get payment statistics using PaymentService."""
        try:
            payment_service = get_payment_service()
            result = payment_service.get_payment_stats(
                days=self.validated_data['days']
            )
            
            if result.success:
                return {
                    'success': True,
                    'stats': result.data,
                    'message': result.message
                }
            else:
                return {
                    'success': False,
                    'error': result.message,
                    'error_code': result.error_code
                }
                
        except Exception as e:
            logger.error(f"Payment stats error: {e}")
            return {
                'success': False,
                'error': f"Stats generation failed: {e}",
                'error_code': 'stats_error'
            }
