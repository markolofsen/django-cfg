"""
Balance Service - Core balance management and transaction processing.

This service handles user balance operations, transaction recording,
and balance validation with atomic operations.
"""

from typing import Dict, Any, Optional, List
from django_cfg.modules.django_logger import get_logger
from decimal import Decimal
from datetime import timezone

from django.db import transaction
from django.contrib.auth import get_user_model
from pydantic import BaseModel, Field, ValidationError

from ...models import UserBalance, Transaction
from ..internal_types import ServiceOperationResult, BalanceUpdateRequest, UserBalanceResult, TransactionInfo

User = get_user_model()
logger = get_logger("balance_service")


class BalanceOperation(BaseModel):
    """Type-safe balance operation request"""
    user_id: int = Field(gt=0, description="User ID")
    amount: Decimal = Field(gt=0, description="Operation amount")
    currency_code: str = Field(default='USD', min_length=3, max_length=10, description="Currency code")
    source: str = Field(min_length=1, description="Operation source")
    reference_id: Optional[str] = Field(None, description="External reference ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class BalanceResult(BaseModel):
    """Type-safe balance operation result"""
    success: bool
    transaction_id: Optional[str] = None
    balance_id: Optional[str] = None
    old_balance: Decimal = Field(default=Decimal('0'))
    new_balance: Decimal = Field(default=Decimal('0'))
    error_message: Optional[str] = None
    error_code: Optional[str] = None


class HoldOperation(BaseModel):
    """Type-safe hold operation request"""
    user_id: int = Field(gt=0, description="User ID")
    amount: Decimal = Field(gt=0, description="Hold amount")
    reason: str = Field(min_length=1, description="Hold reason")
    expires_in_hours: int = Field(default=24, ge=1, le=168, description="Hold expiration in hours")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class BalanceService:
    """
    Universal balance management service.
    
    Handles balance operations, transaction recording, and hold management
    with Redis caching and atomic database operations.
    """
    
    def __init__(self):
        """Initialize balance service with dependencies"""
        pass
    
    def add_funds(
        self,
        user: User,
        amount: Decimal,
        currency_code: str = 'USD',
        source: str = 'manual',
        reference_id: Optional[str] = None,
        **kwargs
    ) -> BalanceResult:
        """
        Add funds to user balance atomically.
        
        Args:
            user: User object
            amount: Amount to add
            currency_code: Currency code (default: USD)
            source: Source of funds (e.g., 'payment', 'manual')
            reference_id: External reference ID
            **kwargs: Additional metadata
            
        Returns:
            BalanceResult with operation status
        """
        try:
            # Validate operation
            operation = BalanceOperation(
                user_id=user.id,
                amount=amount,
                currency_code=currency_code,
                source=source,
                reference_id=reference_id,
                metadata=kwargs
                )
            
            with transaction.atomic():
                # Get or create balance
                balance, created = UserBalance.objects.get_or_create(
                    user=user,
                    defaults={
                        'amount_usd': Decimal('0'),
                        'reserved_usd': Decimal('0')
                    }
                )
                
                old_balance = balance.amount_usd
                
                # Update balance
                balance.amount_usd += float(amount)
                balance.save(update_fields=['amount_usd', 'updated_at'])
                
                # Create transaction record
                transaction_record = Transaction.objects.create(
                    user=user,
                    transaction_type=Transaction.TransactionType.CREDIT,
                    amount_usd=float(amount),
                    balance_before=old_balance,
                    balance_after=balance.amount_usd,
                    description=f"Funds added: {source}",
                    reference_id=reference_id,
                    metadata=kwargs
                )
                
                
                return BalanceResult(
                    success=True,
                    transaction_id=str(transaction_record.id),
                    balance_id=str(balance.id),
                    old_balance=old_balance,
                    new_balance=balance.amount_usd
                )
                
        except ValidationError as e:
            logger.error(f"Balance operation validation error: {e}")
            return BalanceResult(
                success=False,
                error_code='VALIDATION_ERROR',
                error_message=f"Invalid operation data: {e}"
            )
        except Exception as e:
            logger.error(f"Add funds failed for user {user.id}: {e}", exc_info=True)
            return BalanceResult(
                success=False,
                error_code='INTERNAL_ERROR',
                error_message=f"Internal error: {str(e)}"
            )
    
    def deduct_funds(
        self,
        user: User,
        amount: Decimal,
        currency_code: str = 'USD',
        source: str = 'usage',
        reference_id: Optional[str] = None,
        force: bool = False,
        **kwargs
    ) -> BalanceResult:
        """
        Deduct funds from user balance with insufficient funds check.
        
        Args:
            user: User object
            amount: Amount to deduct
            currency_code: Currency code (default: USD)
            source: Source of deduction (e.g., 'usage', 'subscription')
            reference_id: External reference ID
            force: Force deduction even if insufficient funds
            **kwargs: Additional metadata
            
        Returns:
            BalanceResult with operation status
        """
        try:
            # Validate operation
            operation = BalanceOperation(
                user_id=user.id,
                amount=amount,
                currency_code=currency_code,
                source=source,
                reference_id=reference_id,
                metadata=kwargs
            )
            
            with transaction.atomic():
                # Get balance
                try:
                    balance = UserBalance.objects.get(
                        user=user
                    )
                except UserBalance.DoesNotExist:
                    return BalanceResult(
                        success=False,
                        error_code='BALANCE_NOT_FOUND',
                        error_message=f"No balance found for currency {currency_code}"
                    )
                
                old_balance = balance.amount_usd
                
                # Check sufficient funds
                if not force and balance.amount_usd < amount:
                    return BalanceResult(
                        success=False,
                        error_code='INSUFFICIENT_FUNDS',
                        error_message=f"Insufficient funds: available {balance.amount_usd}, required {amount}",
                        old_balance=old_balance,
                        new_balance=old_balance
                    )
                
                # Update balance
                balance.amount_usd -= float(amount)
                balance.save(update_fields=['amount_usd', 'updated_at'])
                
                # Create transaction record
                transaction_record = Transaction.objects.create(
                    user=user,
                    transaction_type=Transaction.TransactionType.DEBIT,
                    amount_usd=-float(amount),  # Negative for debit
                    balance_before=old_balance,
                    balance_after=balance.amount_usd,
                    description=f"Funds deducted: {source}",
                    reference_id=reference_id,
                    metadata=kwargs
                )
                
                
                return BalanceResult(
                    success=True,
                    transaction_id=str(transaction_record.id),
                    balance_id=str(balance.id),
                    old_balance=old_balance,
                    new_balance=balance.amount_usd
                )
                
        except ValidationError as e:
            logger.error(f"Balance operation validation error: {e}")
            return BalanceResult(
                success=False,
                error_code='VALIDATION_ERROR',
                error_message=f"Invalid operation data: {e}"
            )
        except Exception as e:
            logger.error(f"Deduct funds failed for user {user.id}: {e}", exc_info=True)
            return BalanceResult(
                success=False,
                error_code='INTERNAL_ERROR',
                error_message=f"Internal error: {str(e)}"
            )
    
    def transfer_funds(
        self,
        from_user: User,
        to_user: User,
        amount: Decimal,
        currency_code: str = 'USD',
        source: str = 'transfer',
        reference_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Transfer funds between users atomically.
        
        Args:
            from_user: Source user
            to_user: Destination user
            amount: Amount to transfer
            currency_code: Currency code (default: USD)
            source: Transfer source description
            reference_id: External reference ID
            **kwargs: Additional metadata
            
        Returns:
            Transfer result with both transaction IDs
        """
        try:
            with transaction.atomic():
                # Deduct from source user
                deduct_result = self.deduct_funds(
                    user=from_user,
                    amount=amount,
                    currency_code=currency_code,
                    source=f"transfer_out:{source}",
                    reference_id=reference_id,
                    transfer_to_user_id=to_user.id,
                    **kwargs
                )
                
                if not deduct_result.success:
                    return BalanceResult(
                        success=False,
                        error_code=deduct_result.error_code,
                        error_message=deduct_result.error_message
                    )
                
                # Add to destination user
                add_result = self.add_funds(
                    user=to_user,
                    amount=amount,
                    currency_code=currency_code,
                    source=f"transfer_in:{source}",
                    reference_id=reference_id,
                    transfer_from_user_id=from_user.id,
                    **kwargs
                )
                
                if not add_result.success:
                    # This should rarely happen due to atomic transaction
                    logger.error(f"Transfer completion failed: {add_result.error_message}")
                    return BalanceResult(
                        success=False,
                        error_code='TRANSFER_COMPLETION_FAILED',
                        error_message='Transfer could not be completed'
                    )
                
                return BalanceResult(
                    success=True,
                    from_transaction_id=deduct_result.transaction_id,
                    to_transaction_id=add_result.transaction_id,
                    amount_transferred=amount,
                    currency_code=currency_code
                )
                
        except Exception as e:
            logger.error(f"Transfer failed from {from_user.id} to {to_user.id}: {e}", exc_info=True)
            return BalanceResult(
                success=False,
                error_code='INTERNAL_ERROR',
                error_message=f"Transfer failed: {str(e)}"
            )
    
    def get_user_balance(
        self,
        user_id: int,
        currency_code: str = 'USD'
    ) -> Optional['UserBalanceResult']:
        """
        Get user balance.
        
        Args:
            user_id: User ID
            currency_code: Currency code (default: USD)
            
        Returns:
            Balance information or None if not found
        """
        try:
            
            # Get from database
            balance = UserBalance.objects.get(
                user_id=user_id
            )
            
            return UserBalanceResult(
                id=str(balance.id),
                user_id=user_id,
                available_balance=Decimal(str(balance.amount_usd)),
                total_balance=Decimal(str(balance.amount_usd + balance.reserved_usd)),
                reserved_balance=Decimal(str(balance.reserved_usd)),
                last_updated=balance.updated_at,
                created_at=balance.created_at
            )
            
        except UserBalance.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error getting balance for user {user_id}: {e}")
            return None
    
    def get_user_transactions(
        self,
        user: User,
        currency_code: Optional[str] = None,
        transaction_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[TransactionInfo]:
        """
        Get user transaction history.
        
        Args:
            user: User object
            currency_code: Filter by currency code
            transaction_type: Filter by transaction type
            limit: Number of transactions to return
            offset: Pagination offset
            
        Returns:
            List of TransactionInfo objects
        """
        try:
            queryset = Transaction.objects.filter(user=user)
            
            if currency_code:
                queryset = queryset.filter(currency_code=currency_code)
            
            if transaction_type:
                queryset = queryset.filter(transaction_type=transaction_type)
            
            transactions = queryset.order_by('-created_at')[offset:offset+limit]
            
            return [
                TransactionInfo(
                    id=str(txn.id),
                    user_id=txn.user.id,
                    transaction_type=txn.transaction_type,
                    amount=txn.amount,
                    balance_after=txn.balance_after,
                    source=txn.source,
                    reference_id=txn.reference_id,
                    description=txn.description,
                    created_at=txn.created_at
                )
                for txn in transactions
            ]
            
        except Exception as e:
            logger.error(f"Error getting transactions for user {user.id}: {e}")
            return []
    
    
    # Alias methods for backward compatibility with tests
    def credit_balance(self, request: 'BalanceUpdateRequest') -> 'ServiceOperationResult':
        """Alias for add_funds method."""
        
        user = User.objects.get(id=request.user_id)
        return self.add_funds(
            user=user,
            amount=request.amount,
            source=request.source,
            reference_id=request.reference_id,
            description=getattr(request, 'description', None)
        )
    
    def debit_balance(self, request: 'BalanceUpdateRequest') -> 'ServiceOperationResult':
        """Alias for deduct_funds method."""

        user = User.objects.get(id=request.user_id)
        return self.deduct_funds(
            user=user,
            amount=request.amount,
            reason=request.source,
            reference_id=request.reference_id,
            description=getattr(request, 'description', None)
        )
