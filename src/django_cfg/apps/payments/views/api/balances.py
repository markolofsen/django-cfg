"""
Balance ViewSets for the Universal Payment System v2.0.

DRF ViewSets for balance and transaction management with service integration.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.db import models

from .base import PaymentBaseViewSet, NestedPaymentViewSet, ReadOnlyPaymentViewSet
from ...models import UserBalance, Transaction
from ...services import get_balance_service
from ..serializers.balances import (
    UserBalanceSerializer,
    TransactionSerializer,
    BalanceUpdateSerializer,
    FundsTransferSerializer,
    BalanceStatsSerializer,
)
from django_cfg.modules.django_logger import get_logger

User = get_user_model()
logger = get_logger("balance_viewsets")


class UserBalanceViewSet(ReadOnlyPaymentViewSet):
    """
    User balance ViewSet: /api/balances/
    
    Read-only access to user balances with statistics.
    """
    
    queryset = UserBalance.objects.all()
    serializer_class = UserBalanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['user']
    search_fields = ['user__username', 'user__email']
    ordering_fields = ['balance_usd', 'created_at', 'updated_at']
    
    def get_queryset(self):
        """Filter by user permissions and optimize queryset."""
        queryset = super().get_queryset().select_related('user')
        
        # Non-staff users can only see their own balance
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def add_funds(self, request, pk=None):
        """
        Add funds to user balance.
        
        POST /api/balances/{id}/add_funds/
        """
        balance = self.get_object()
        
        # Permission check: users can only add funds to their own balance
        if not request.user.is_staff and balance.user != request.user:
            return Response(
                {'error': 'You can only add funds to your own balance'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = BalanceUpdateSerializer(
            data=request.data,
            context={
                **self.get_serializer_context(),
                'user_pk': balance.user.id
            }
        )
        
        if serializer.is_valid():
            result = serializer.save()
            return Response(result)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def withdraw_funds(self, request, pk=None):
        """
        Withdraw funds from user balance.
        
        POST /api/balances/{id}/withdraw_funds/
        """
        balance = self.get_object()
        
        # Permission check
        if not request.user.is_staff and balance.user != request.user:
            return Response(
                {'error': 'You can only withdraw from your own balance'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Convert to negative amount for withdrawal
        data = request.data.copy()
        if 'amount' in data and data['amount'] > 0:
            data['amount'] = -abs(data['amount'])
        
        serializer = BalanceUpdateSerializer(
            data=data,
            context={
                **self.get_serializer_context(),
                'user_pk': balance.user.id
            }
        )
        
        if serializer.is_valid():
            result = serializer.save()
            return Response(result)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def transfer_funds(self, request, pk=None):
        """
        Transfer funds to another user.
        
        POST /api/balances/{id}/transfer_funds/
        """
        balance = self.get_object()
        
        # Permission check
        if not request.user.is_staff and balance.user != request.user:
            return Response(
                {'error': 'You can only transfer from your own balance'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = FundsTransferSerializer(
            data=request.data,
            context=self.get_serializer_context()
        )
        
        if serializer.is_valid():
            result = serializer.save()
            return Response(result)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """
        Get balance analytics.
        
        GET /api/balances/analytics/?days=30
        """
        serializer = BalanceStatsSerializer(data=request.query_params)
        
        if serializer.is_valid():
            result = serializer.save()
            return Response(result)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get balance summary for all users.
        
        GET /api/balances/summary/
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            summary = queryset.aggregate(
                total_users=models.Count('id'),
                total_balance=models.Sum('balance_usd'),
                average_balance=models.Avg('balance_usd'),
                users_with_balance=models.Count(
                    'id',
                    filter=models.Q(balance_usd__gt=0)
                ),
                empty_balances=models.Count(
                    'id',
                    filter=models.Q(balance_usd=0)
                ),
            )
            
            return Response({
                'summary': {
                    **summary,
                    'total_balance': float(summary['total_balance'] or 0),
                    'average_balance': float(summary['average_balance'] or 0),
                },
                'generated_at': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Balance summary failed: {e}")
            return Response(
                {'error': f'Summary generation failed: {e}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TransactionViewSet(ReadOnlyPaymentViewSet):
    """
    Transaction ViewSet: /api/transactions/
    
    Read-only access to transaction history with filtering.
    """
    
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['user', 'transaction_type', 'payment_id']
    search_fields = ['description', 'payment_id']
    ordering_fields = ['created_at', 'amount']
    
    def get_queryset(self):
        """Filter by user permissions and optimize queryset."""
        queryset = super().get_queryset().select_related('user')
        
        # Non-staff users can only see their own transactions
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """
        Get transactions grouped by type.
        
        GET /api/transactions/by_type/
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            type_stats = {}
            for type_choice in Transaction.TransactionType.choices:
                type_code = type_choice[0]
                type_name = type_choice[1]
                
                type_transactions = queryset.filter(transaction_type=type_code)
                
                type_stats[type_code] = {
                    'name': type_name,
                    'total_transactions': type_transactions.count(),
                    'total_amount': float(
                        type_transactions.aggregate(
                            total=models.Sum('amount')
                        )['total'] or 0
                    ),
                    'average_amount': float(
                        type_transactions.aggregate(
                            avg=models.Avg('amount')
                        )['avg'] or 0
                    ),
                }
            
            return Response({
                'type_stats': type_stats,
                'generated_at': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Transaction type stats failed: {e}")
            return Response(
                {'error': f'Type stats failed: {e}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Get recent transactions.
        
        GET /api/transactions/recent/?limit=10
        """
        try:
            limit = int(request.query_params.get('limit', 10))
            limit = min(limit, 100)  # Cap at 100
            
            queryset = self.filter_queryset(self.get_queryset())
            recent_transactions = queryset.order_by('-created_at')[:limit]
            
            serializer = self.get_serializer(recent_transactions, many=True)
            
            return Response({
                'transactions': serializer.data,
                'count': len(serializer.data),
                'limit': limit,
                'generated_at': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Recent transactions failed: {e}")
            return Response(
                {'error': f'Recent transactions failed: {e}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserTransactionViewSet(NestedPaymentViewSet):
    """
    User-specific transaction ViewSet: /api/users/{user_id}/transactions/
    
    User-scoped access to transaction history.
    """
    
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['transaction_type', 'payment_id']
    search_fields = ['description', 'payment_id']
    ordering_fields = ['created_at', 'amount']
    
    # Nested ViewSet configuration
    parent_lookup_field = 'user_pk'
    parent_model_field = 'user'
    
    # Read-only operations only
    http_method_names = ['get', 'head', 'options']
    
    def get_queryset(self):
        """Filter by user and optimize queryset."""
        queryset = super().get_queryset()
        
        # Additional permission check: users can only see their own transactions
        if not self.request.user.is_staff:
            user_id = self.kwargs.get('user_pk')
            if str(self.request.user.id) != str(user_id):
                return queryset.none()
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def summary(self, request, user_pk=None):
        """
        Get user transaction summary.
        
        GET /api/users/{user_id}/transactions/summary/
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            summary = queryset.aggregate(
                total_transactions=models.Count('id'),
                total_credits=models.Sum(
                    'amount',
                    filter=models.Q(amount__gt=0)
                ),
                total_debits=models.Sum(
                    'amount',
                    filter=models.Q(amount__lt=0)
                ),
                net_amount=models.Sum('amount'),
            )
            
            # Get type breakdown
            type_breakdown = dict(
                queryset.values('transaction_type')
                .annotate(count=models.Count('id'))
                .values_list('transaction_type', 'count')
            )
            
            return Response({
                'user_id': user_pk,
                'summary': {
                    **summary,
                    'total_credits': float(summary['total_credits'] or 0),
                    'total_debits': float(abs(summary['total_debits'] or 0)),
                    'net_amount': float(summary['net_amount'] or 0),
                    'type_breakdown': type_breakdown,
                },
                'generated_at': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"User transaction summary failed: {e}")
            return Response(
                {'error': f'Summary generation failed: {e}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
