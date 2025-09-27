"""
Balance serializers for the Universal Payment System v2.0.

DRF serializers for balance and transaction operations with service integration.
"""

from rest_framework import serializers
from decimal import Decimal
from typing import Dict, Any
from django.contrib.auth import get_user_model

from ...models import UserBalance, Transaction
from ...services import get_balance_service, BalanceUpdateRequest
from django_cfg.modules.django_logger import get_logger

User = get_user_model()
logger = get_logger("balance_serializers")


class UserBalanceSerializer(serializers.ModelSerializer):
    """
    User balance serializer with computed fields.
    
    Provides balance information with display helpers.
    """
    
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = UserBalance
        fields = [
            'user',
            'balance_usd',
            'balance_display',
            'is_empty',
            'has_transactions',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class TransactionSerializer(serializers.ModelSerializer):
    """
    Transaction serializer with full details.
    
    Used for transaction history and details.
    """
    
    user = serializers.StringRelatedField(read_only=True)
    amount_display = serializers.CharField(read_only=True)
    type_color = serializers.CharField(read_only=True)
    is_credit = serializers.BooleanField(read_only=True)
    is_debit = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id',
            'user',
            'amount_usd',
            'amount_display',
            'transaction_type',
            'type_color',
            'description',
            'payment_id',
            'metadata',
            'is_credit',
            'is_debit',
            'created_at',
        ]
        read_only_fields = fields


class BalanceUpdateSerializer(serializers.Serializer):
    """
    Balance update serializer with service integration.
    
    Validates and processes balance updates through BalanceService.
    """
    
    amount = serializers.FloatField(
        help_text="Amount to add (positive) or subtract (negative)"
    )
    transaction_type = serializers.ChoiceField(
        choices=[
            ('deposit', 'Deposit'),
            ('withdrawal', 'Withdrawal'),
            ('payment', 'Payment'),
            ('refund', 'Refund'),
            ('fee', 'Fee'),
            ('bonus', 'Bonus'),
            ('adjustment', 'Adjustment'),
        ],
        help_text="Type of transaction"
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        help_text="Transaction description"
    )
    payment_id = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text="Related payment ID"
    )
    metadata = serializers.JSONField(
        required=False,
        default=dict,
        help_text="Additional metadata"
    )
    
    def validate_amount(self, value: float) -> float:
        """Validate amount is not zero."""
        if value == 0:
            raise serializers.ValidationError("Amount cannot be zero")
        return value
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate balance update data."""
        try:
            # Get user from context
            user_id = self.context.get('user_pk') or self.context['request'].user.id
            
            # Create Pydantic request for validation
            request = BalanceUpdateRequest(
                user_id=user_id,
                **attrs
            )
            
            # Store validated request for save method
            self._validated_request = request
            return attrs
            
        except Exception as e:
            logger.error(f"Balance update validation failed: {e}")
            raise serializers.ValidationError(f"Invalid balance update data: {e}")
    
    def save(self) -> Dict[str, Any]:
        """Update balance using BalanceService."""
        try:
            balance_service = get_balance_service()
            result = balance_service.update_balance(self._validated_request)
            
            if result.success:
                logger.info(f"Balance updated successfully", extra={
                    'user_id': self._validated_request.user_id,
                    'amount': self._validated_request.amount,
                    'transaction_id': result.transaction_id
                })
                
                return {
                    'success': True,
                    'message': result.message,
                    'balance': {
                        'user_id': result.user_id,
                        'balance_usd': result.balance_usd,
                        'transaction_id': result.transaction_id,
                        'transaction_amount': result.transaction_amount,
                        'transaction_type': result.transaction_type,
                    }
                }
            else:
                return {
                    'success': False,
                    'error': result.message,
                    'error_code': result.error_code
                }
                
        except Exception as e:
            logger.error(f"Balance update error: {e}")
            return {
                'success': False,
                'error': f"Balance update failed: {e}",
                'error_code': 'balance_update_error'
            }


class FundsTransferSerializer(serializers.Serializer):
    """
    Funds transfer serializer for transferring between users.
    
    Handles user-to-user fund transfers through BalanceService.
    """
    
    to_user_id = serializers.IntegerField(
        min_value=1,
        help_text="Destination user ID"
    )
    amount = serializers.FloatField(
        min_value=0.01,
        help_text="Amount to transfer (must be positive)"
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        help_text="Transfer description"
    )
    
    def validate_to_user_id(self, value: int) -> int:
        """Validate destination user exists."""
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"User {value} not found")
        return value
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate transfer data."""
        from_user_id = self.context['request'].user.id
        to_user_id = attrs['to_user_id']
        
        if from_user_id == to_user_id:
            raise serializers.ValidationError("Cannot transfer to yourself")
        
        return attrs
    
    def save(self) -> Dict[str, Any]:
        """Execute transfer using BalanceService."""
        try:
            from_user_id = self.context['request'].user.id
            to_user_id = self.validated_data['to_user_id']
            amount = self.validated_data['amount']
            description = self.validated_data.get('description')
            
            balance_service = get_balance_service()
            result = balance_service.transfer_funds(
                from_user_id=from_user_id,
                to_user_id=to_user_id,
                amount=amount,
                description=description
            )
            
            if result.success:
                return {
                    'success': True,
                    'message': result.message,
                    'transfer': result.data
                }
            else:
                return {
                    'success': False,
                    'error': result.message,
                    'error_code': result.error_code
                }
                
        except Exception as e:
            logger.error(f"Funds transfer error: {e}")
            return {
                'success': False,
                'error': f"Transfer failed: {e}",
                'error_code': 'transfer_error'
            }


class BalanceStatsSerializer(serializers.Serializer):
    """
    Balance statistics serializer.
    
    Used for balance analytics and reporting.
    """
    
    days = serializers.IntegerField(
        default=30,
        min_value=1,
        max_value=365,
        help_text="Number of days to analyze"
    )
    
    def save(self) -> Dict[str, Any]:
        """Get balance statistics using BalanceService."""
        try:
            balance_service = get_balance_service()
            result = balance_service.get_balance_stats(
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
            logger.error(f"Balance stats error: {e}")
            return {
                'success': False,
                'error': f"Stats generation failed: {e}",
                'error_code': 'stats_error'
            }
