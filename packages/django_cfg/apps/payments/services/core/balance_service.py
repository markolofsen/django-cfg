"""
Balance service for the Universal Payment System v2.0.

Handles user balance operations and transaction management.
"""

from typing import Optional, Dict, Any, List
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()

from .base import BaseService
from ..types import (
    BalanceUpdateRequest, BalanceResult, TransactionData,
    ServiceOperationResult, BalanceData
)
from ...models import UserBalance, Transaction


class BalanceService(BaseService):
    """
    Balance service with business logic and validation.
    
    Handles balance operations using Pydantic validation and Django ORM managers.
    """
    
    def get_user_balance(self, user_id: int) -> BalanceResult:
        """
        Get user balance, creating if doesn't exist.
        
        Args:
            user_id: User ID
            
        Returns:
            BalanceResult: User balance information
        """
        try:
            self.logger.debug("Getting user balance", extra={'user_id': user_id})
            
            # Get or create user
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return BalanceResult(
                    success=False,
                    message=f"User {user_id} not found",
                    error_code="user_not_found"
                )
            
            # Get or create balance using manager
            balance = UserBalance.objects.get_or_create_for_user(user)
            balance_data = BalanceData.model_validate(balance)
            
            self._log_operation(
                "get_user_balance",
                True,
                user_id=user_id,
                balance_usd=balance.balance_usd
            )
            
            return BalanceResult(
                success=True,
                message="Balance retrieved successfully",
                user_id=user_id,
                balance_usd=balance.balance_usd,
                data={'balance': balance_data.model_dump()}
            )
            
        except Exception as e:
            return BalanceResult(**self._handle_exception(
                "get_user_balance", e,
                user_id=user_id
            ).model_dump())
    
    def update_balance(self, request: BalanceUpdateRequest) -> BalanceResult:
        """
        Update user balance with transaction record.
        
        Args:
            request: Balance update request with validation
            
        Returns:
            BalanceResult: Updated balance information
        """
        try:
            # Validate request
            if isinstance(request, dict):
                request = BalanceUpdateRequest(**request)
            
            self.logger.info("Updating user balance", extra={
                'user_id': request.user_id,
                'amount': request.amount,
                'transaction_type': request.transaction_type
            })
            
            # Get user
            try:
                user = User.objects.get(id=request.user_id)
            except User.DoesNotExist:
                return BalanceResult(
                    success=False,
                    message=f"User {request.user_id} not found",
                    error_code="user_not_found"
                )
            
            # Get or create balance
            balance = UserBalance.objects.get_or_create_for_user(user)
            
            # Check for sufficient funds if subtracting
            if request.amount < 0 and balance.balance_usd + request.amount < 0:
                return BalanceResult(
                    success=False,
                    message="Insufficient funds",
                    error_code="insufficient_funds",
                    user_id=request.user_id,
                    balance_usd=balance.balance_usd
                )
            
            # Update balance using manager
            def update_balance_transaction():
                if request.amount > 0:
                    transaction = balance.add_funds(
                        amount=request.amount,
                        transaction_type=request.transaction_type,
                        description=request.description,
                        payment_id=request.payment_id
                    )
                else:
                    transaction = balance.subtract_funds(
                        amount=abs(request.amount),
                        transaction_type=request.transaction_type,
                        description=request.description,
                        payment_id=request.payment_id
                    )
                return transaction
            
            transaction = self._execute_with_transaction(update_balance_transaction)
            
            # Refresh balance
            balance.refresh_from_db()
            
            # Convert to response data
            balance_data = BalanceData.model_validate(balance)
            transaction_data = TransactionData(
                id=str(transaction.id),
                user_id=transaction.user_id,
                amount=float(transaction.amount_usd),
                transaction_type=transaction.transaction_type,
                description=transaction.description,
                payment_id=transaction.payment_id,
                metadata=transaction.metadata or {},
                created_at=transaction.created_at
            )
            
            self._log_operation(
                "update_balance",
                True,
                user_id=request.user_id,
                amount=request.amount,
                new_balance=balance.balance_usd,
                transaction_id=str(transaction.id)
            )
            
            return BalanceResult(
                success=True,
                message="Balance updated successfully",
                user_id=request.user_id,
                balance_usd=balance.balance_usd,
                transaction_id=str(transaction.id),
                transaction_amount=request.amount,
                transaction_type=request.transaction_type,
                data={
                    'balance': balance_data.model_dump(),
                    'transaction': transaction_data.model_dump()
                }
            )
            
        except Exception as e:
            return BalanceResult(**self._handle_exception(
                "update_balance", e,
                user_id=request.user_id if hasattr(request, 'user_id') else None
            ).model_dump())
    
    def add_funds(
        self, 
        user_id: int, 
        amount: float, 
        description: str = None,
        payment_id: str = None
    ) -> BalanceResult:
        """
        Add funds to user balance.
        
        Args:
            user_id: User ID
            amount: Amount to add (positive)
            description: Transaction description
            payment_id: Related payment ID
            
        Returns:
            BalanceResult: Updated balance
        """
        request = BalanceUpdateRequest(
            user_id=user_id,
            amount=abs(amount),  # Ensure positive
            transaction_type='deposit',
            description=description,
            payment_id=payment_id
        )
        return self.update_balance(request)
    
    def subtract_funds(
        self,
        user_id: int,
        amount: float,
        description: str = None,
        payment_id: str = None
    ) -> BalanceResult:
        """
        Subtract funds from user balance.
        
        Args:
            user_id: User ID
            amount: Amount to subtract (positive)
            description: Transaction description
            payment_id: Related payment ID
            
        Returns:
            BalanceResult: Updated balance
        """
        request = BalanceUpdateRequest(
            user_id=user_id,
            amount=-abs(amount),  # Ensure negative
            transaction_type='withdrawal',
            description=description,
            payment_id=payment_id
        )
        return self.update_balance(request)
    
    def get_user_transactions(
        self,
        user_id: int,
        transaction_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> ServiceOperationResult:
        """
        Get user transaction history.
        
        Args:
            user_id: User ID
            transaction_type: Filter by transaction type
            limit: Number of transactions to return
            offset: Pagination offset
            
        Returns:
            ServiceOperationResult: Transaction list
        """
        try:
            self.logger.debug("Getting user transactions", extra={
                'user_id': user_id,
                'transaction_type': transaction_type,
                'limit': limit,
                'offset': offset
            })
            
            # Check user exists
            if not User.objects.filter(id=user_id).exists():
                return self._create_error_result(
                    f"User {user_id} not found",
                    "user_not_found"
                )
            
            # Build query
            queryset = Transaction.objects.filter(user_id=user_id)
            
            if transaction_type:
                queryset = queryset.filter(transaction_type=transaction_type)
            
            # Get total count
            total_count = queryset.count()
            
            # Get transactions with pagination
            transactions = queryset.order_by('-created_at')[offset:offset + limit]
            
            # Convert to data
            transaction_data = [
                TransactionData.model_validate(transaction).model_dump()
                for transaction in transactions
            ]
            
            return self._create_success_result(
                f"Retrieved {len(transaction_data)} transactions",
                {
                    'transactions': transaction_data,
                    'total_count': total_count,
                    'limit': limit,
                    'offset': offset,
                    'has_more': offset + limit < total_count
                }
            )
            
        except Exception as e:
            return self._handle_exception(
                "get_user_transactions", e,
                user_id=user_id
            )
    
    def get_balance_stats(self, days: int = 30) -> ServiceOperationResult:
        """
        Get balance and transaction statistics.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            ServiceOperationResult: Balance statistics
        """
        try:
            from datetime import timedelta
            
            since = timezone.now() - timedelta(days=days)
            
            # Balance stats
            balance_stats = UserBalance.objects.aggregate(
                total_users=models.Count('user_id'),
                total_balance=models.Sum('balance_usd'),
                avg_balance=models.Avg('balance_usd'),
                max_balance=models.Max('balance_usd'),
                users_with_balance=models.Count(
                    'user_id',
                    filter=models.Q(balance_usd__gt=0)
                )
            )
            
            # Transaction stats
            transaction_stats = Transaction.objects.filter(
                created_at__gte=since
            ).aggregate(
                total_transactions=models.Count('id'),
                total_volume=models.Sum('amount'),
                deposits=models.Sum(
                    'amount',
                    filter=models.Q(transaction_type='deposit')
                ),
                withdrawals=models.Sum(
                    'amount',
                    filter=models.Q(transaction_type='withdrawal')
                ),
                avg_transaction=models.Avg('amount')
            )
            
            # Transaction type breakdown
            type_breakdown = Transaction.objects.filter(
                created_at__gte=since
            ).values('transaction_type').annotate(
                count=models.Count('id'),
                volume=models.Sum('amount')
            ).order_by('-count')
            
            stats = {
                'period_days': days,
                'balance_stats': balance_stats,
                'transaction_stats': transaction_stats,
                'transaction_types': list(type_breakdown),
                'generated_at': timezone.now().isoformat()
            }
            
            return self._create_success_result(
                f"Balance statistics for {days} days",
                stats
            )
            
        except Exception as e:
            return self._handle_exception("get_balance_stats", e)
    
    def transfer_funds(
        self,
        from_user_id: int,
        to_user_id: int,
        amount: float,
        description: str = None
    ) -> ServiceOperationResult:
        """
        Transfer funds between users.
        
        Args:
            from_user_id: Source user ID
            to_user_id: Destination user ID
            amount: Amount to transfer
            description: Transfer description
            
        Returns:
            ServiceOperationResult: Transfer result
        """
        try:
            if amount <= 0:
                return self._create_error_result(
                    "Transfer amount must be positive",
                    "invalid_amount"
                )
            
            if from_user_id == to_user_id:
                return self._create_error_result(
                    "Cannot transfer to same user",
                    "same_user_transfer"
                )
            
            self.logger.info("Transferring funds", extra={
                'from_user_id': from_user_id,
                'to_user_id': to_user_id,
                'amount': amount
            })
            
            # Check both users exist
            if not User.objects.filter(id=from_user_id).exists():
                return self._create_error_result(
                    f"Source user {from_user_id} not found",
                    "source_user_not_found"
                )
            
            if not User.objects.filter(id=to_user_id).exists():
                return self._create_error_result(
                    f"Destination user {to_user_id} not found",
                    "destination_user_not_found"
                )
            
            # Execute transfer in transaction
            def transfer_transaction():
                # Subtract from source
                subtract_result = self.subtract_funds(
                    from_user_id,
                    amount,
                    f"Transfer to user {to_user_id}: {description}" if description else f"Transfer to user {to_user_id}"
                )
                
                if not subtract_result.success:
                    raise ValueError(subtract_result.message)
                
                # Add to destination
                add_result = self.add_funds(
                    to_user_id,
                    amount,
                    f"Transfer from user {from_user_id}: {description}" if description else f"Transfer from user {from_user_id}"
                )
                
                if not add_result.success:
                    raise ValueError(add_result.message)
                
                return {
                    'from_transaction': subtract_result.transaction_id,
                    'to_transaction': add_result.transaction_id,
                    'from_balance': subtract_result.balance_usd,
                    'to_balance': add_result.balance_usd
                }
            
            result = self._execute_with_transaction(transfer_transaction)
            
            self._log_operation(
                "transfer_funds",
                True,
                from_user_id=from_user_id,
                to_user_id=to_user_id,
                amount=amount
            )
            
            return self._create_success_result(
                "Funds transferred successfully",
                {
                    'from_user_id': from_user_id,
                    'to_user_id': to_user_id,
                    'amount': amount,
                    'from_transaction_id': result['from_transaction'],
                    'to_transaction_id': result['to_transaction'],
                    'from_balance': result['from_balance'],
                    'to_balance': result['to_balance']
                }
            )
            
        except Exception as e:
            return self._handle_exception(
                "transfer_funds", e,
                from_user_id=from_user_id,
                to_user_id=to_user_id,
                amount=amount
            )
    
    def freeze_balance(self, user_id: int, amount: float, reason: str) -> ServiceOperationResult:
        """
        Freeze part of user balance (for future implementation).
        
        Args:
            user_id: User ID
            amount: Amount to freeze
            reason: Freeze reason
            
        Returns:
            ServiceOperationResult: Freeze result
        """
        # Placeholder for future frozen balance functionality
        return self._create_error_result(
            "Balance freezing not yet implemented",
            "not_implemented"
        )
    
    def health_check(self) -> ServiceOperationResult:
        """Perform balance service health check."""
        try:
            # Check database connectivity
            balance_count = UserBalance.objects.count()
            transaction_count = Transaction.objects.count()
            
            # Check for recent activity
            recent_transactions = Transaction.objects.filter(
                created_at__gte=timezone.now() - timezone.timedelta(hours=1)
            ).count()
            
            stats = {
                'total_balances': balance_count,
                'total_transactions': transaction_count,
                'recent_transactions': recent_transactions,
                'service_name': 'BalanceService'
            }
            
            return self._create_success_result(
                "BalanceService is healthy",
                stats
            )
            
        except Exception as e:
            return self._handle_exception("health_check", e)
