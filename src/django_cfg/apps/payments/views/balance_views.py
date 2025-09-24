"""
Balance ViewSets.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from ..models import UserBalance, Transaction
from ..serializers import (
    UserBalanceSerializer, TransactionSerializer, TransactionListSerializer
)


class UserBalanceViewSet(viewsets.ReadOnlyModelViewSet):
    """User balance ViewSet - read only."""
    
    queryset = UserBalance.objects.all()
    serializer_class = UserBalanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter by current user."""
        return UserBalance.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current user balance."""
        balance, _ = UserBalance.objects.get_or_create(
            user=request.user,
            defaults={'amount_usd': 0.0, 'reserved_usd': 0.0}
        )
        serializer = self.get_serializer(balance)
        return Response(serializer.data)


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """Transaction ViewSet - read only."""
    
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['transaction_type', 'payment', 'subscription']
    
    def get_queryset(self):
        """Filter by current user."""
        return Transaction.objects.filter(user=self.request.user).order_by('-created_at')
    
    def get_serializer_class(self):
        """Use list serializer for list action."""
        if self.action == 'list':
            return TransactionListSerializer
        return TransactionSerializer
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get transaction summary."""
        queryset = self.get_queryset()
        
        total_earned = sum(
            t.amount_usd for t in queryset 
            if t.amount_usd > 0
        )
        total_spent = sum(
            abs(t.amount_usd) for t in queryset 
            if t.amount_usd < 0
        )
        
        return Response({
            'total_transactions': queryset.count(),
            'total_earned': total_earned,
            'total_spent': total_spent,
            'net_balance': total_earned - total_spent
        })
