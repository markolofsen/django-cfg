"""
Balance serializers.
"""

from rest_framework import serializers
from ..models import UserBalance, Transaction


class UserBalanceSerializer(serializers.ModelSerializer):
    """User balance with computed fields."""
    
    total_balance = serializers.ReadOnlyField()
    pending_payments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = UserBalance
        fields = [
            'amount_usd', 'reserved_usd', 'total_balance',
            'total_earned', 'total_spent', 'last_transaction_at',
            'pending_payments_count', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'total_earned', 'total_spent', 'last_transaction_at',
            'created_at', 'updated_at'
        ]
    
    def get_pending_payments_count(self, obj):
        """Get count of pending payments."""
        return obj.user.universal_payments.filter(status='pending').count()


class TransactionSerializer(serializers.ModelSerializer):
    """Transaction with details."""
    
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    is_credit = serializers.ReadOnlyField()
    is_debit = serializers.ReadOnlyField()
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'amount_usd', 'transaction_type', 'transaction_type_display',
            'description', 'balance_before', 'balance_after', 
            'is_credit', 'is_debit', 'reference_id', 'created_at'
        ]
        read_only_fields = ['id', 'balance_before', 'balance_after', 'created_at']


class TransactionListSerializer(serializers.ModelSerializer):
    """Simplified transaction for lists."""
    
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'amount_usd', 'transaction_type', 'transaction_type_display',
            'description', 'balance_after', 'created_at'
        ]
