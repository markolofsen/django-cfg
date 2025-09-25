"""
User balance manager with atomic operations.

Following CRITICAL_REQUIREMENTS.md:
- Atomic balance updates
- Type safety 
- Event sourcing
- Proper error handling
"""

from django.db import models, transaction
from django.utils import timezone
from decimal import Decimal
from typing import Optional, Dict, Any
from django_cfg.modules.django_logger import get_logger

logger = get_logger("balance_manager")


class UserBalanceManager(models.Manager):
    """Manager for UserBalance with atomic operations."""
    
    def get_or_create_balance(self, user) -> 'UserBalance':
        """Get or create user balance atomically."""
        balance, created = self.get_or_create(
            user=user,
            defaults={
                'amount_usd': Decimal('0'),
                'reserved_usd': Decimal('0'),
                'total_earned': Decimal('0'),
                'total_spent': Decimal('0'),
            }
        )
        
        if created:
            logger.info(f"Created new balance for user {user.id}")
        
        return balance
    
    def add_funds(
        self, 
        user,
        amount_usd: Decimal,
        description: str,
        reference_id: Optional[str] = None,
        payment=None
    ) -> Dict[str, Any]:
        """
        Add funds to user balance atomically.
        
        Returns:
            Dict with operation result and transaction details
        """
        if amount_usd <= 0:
            raise ValueError("Amount must be positive")
        
        with transaction.atomic():
            # Get or create balance with row lock
            balance = self.select_for_update().get_or_create_balance(user)
            
            # Store old values for transaction record
            old_balance = balance.amount_usd
            old_earned = balance.total_earned
            
            # Update balance
            balance.amount_usd += amount_usd
            balance.total_earned += amount_usd
            balance.last_transaction_at = timezone.now()
            balance.save()
            
            # Create transaction record
            from ..models.balance import Transaction
            transaction_record = Transaction.objects.create(
                user=user,
                amount_usd=amount_usd,
                transaction_type=Transaction.TypeChoices.CREDIT,
                description=description,
                payment=payment,
                reference_id=reference_id,
                balance_before=old_balance,
                balance_after=balance.amount_usd,
                metadata={
                    'total_earned_before': str(old_earned),
                    'total_earned_after': str(balance.total_earned),
                }
            )
            
            logger.info(
                f"Added ${amount_usd} to user {user.id} balance. "
                f"New balance: ${balance.amount_usd}"
            )
            
            return {
                'success': True,
                'old_balance': old_balance,
                'new_balance': balance.amount_usd,
                'amount_added': amount_usd,
                'transaction_id': str(transaction_record.id),
                'balance_obj': balance
            }
    
    def debit_funds(
        self,
        user,
        amount_usd: Decimal,
        description: str,
        reference_id: Optional[str] = None,
        allow_overdraft: bool = False
    ) -> Dict[str, Any]:
        """
        Debit funds from user balance atomically.
        
        Args:
            user: User object
            amount_usd: Amount to debit (positive value)
            description: Transaction description
            reference_id: Optional reference ID
            allow_overdraft: Allow negative balance
            
        Returns:
            Dict with operation result
        """
        if amount_usd <= 0:
            raise ValueError("Amount must be positive")
        
        with transaction.atomic():
            # Get balance with row lock
            balance = self.select_for_update().get_or_create_balance(user)
            
            # Check sufficient funds
            if not allow_overdraft and balance.amount_usd < amount_usd:
                from ..models.exceptions import InsufficientFundsError
                from ..models.pydantic_models import MoneyAmount
                from ..models import CurrencyChoices
                
                raise InsufficientFundsError(
                    message=f"Insufficient funds: ${balance.amount_usd} < ${amount_usd}",
                    required_amount=MoneyAmount(amount=amount_usd, currency=CurrencyChoices.USD),
                    available_amount=MoneyAmount(amount=balance.amount_usd, currency=CurrencyChoices.USD),
                    user_id=user.id
                )
            
            # Store old values
            old_balance = balance.amount_usd
            old_spent = balance.total_spent
            
            # Update balance
            balance.amount_usd -= amount_usd
            balance.total_spent += amount_usd
            balance.last_transaction_at = timezone.now()
            balance.save()
            
            # Create transaction record
            from ..models.balance import Transaction
            transaction_record = Transaction.objects.create(
                user=user,
                amount_usd=-amount_usd,  # Negative for debit
                transaction_type=Transaction.TypeChoices.DEBIT,
                description=description,
                reference_id=reference_id,
                balance_before=old_balance,
                balance_after=balance.amount_usd,
                metadata={
                    'total_spent_before': str(old_spent),
                    'total_spent_after': str(balance.total_spent),
                    'allow_overdraft': allow_overdraft,
                }
            )
            
            logger.info(
                f"Debited ${amount_usd} from user {user.id} balance. "
                f"New balance: ${balance.amount_usd}"
            )
            
            return {
                'success': True,
                'old_balance': old_balance,
                'new_balance': balance.amount_usd,
                'amount_debited': amount_usd,
                'transaction_id': str(transaction_record.id),
                'balance_obj': balance
            }
    
    def hold_funds(
        self,
        user,
        amount_usd: Decimal,
        description: str,
        reference_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Hold funds (move from available to reserved).
        
        Args:
            user: User object
            amount_usd: Amount to hold
            description: Hold description
            reference_id: Optional reference ID
            
        Returns:
            Dict with operation result
        """
        if amount_usd <= 0:
            raise ValueError("Amount must be positive")
        
        with transaction.atomic():
            # Get balance with row lock
            balance = self.select_for_update().get_or_create_balance(user)
            
            # Check sufficient available funds
            if balance.amount_usd < amount_usd:
                from ..models.exceptions import InsufficientFundsError
                from ..models.pydantic_models import MoneyAmount
                from ..models import CurrencyChoices
                
                raise InsufficientFundsError(
                    message=f"Insufficient available funds for hold: ${balance.amount_usd} < ${amount_usd}",
                    required_amount=MoneyAmount(amount=amount_usd, currency=CurrencyChoices.USD),
                    available_amount=MoneyAmount(amount=balance.amount_usd, currency=CurrencyChoices.USD),
                    user_id=user.id
                )
            
            # Store old values
            old_available = balance.amount_usd
            old_reserved = balance.reserved_usd
            
            # Move funds from available to reserved
            balance.amount_usd -= amount_usd
            balance.reserved_usd += amount_usd
            balance.last_transaction_at = timezone.now()
            balance.save()
            
            # Create transaction record
            from ..models.balance import Transaction
            transaction_record = Transaction.objects.create(
                user=user,
                amount_usd=amount_usd,
                transaction_type=Transaction.TypeChoices.HOLD,
                description=description,
                reference_id=reference_id,
                balance_before=old_available,
                balance_after=balance.amount_usd,
                metadata={
                    'reserved_before': str(old_reserved),
                    'reserved_after': str(balance.reserved_usd),
                    'operation': 'hold_funds',
                }
            )
            
            logger.info(
                f"Held ${amount_usd} for user {user.id}. "
                f"Available: ${balance.amount_usd}, Reserved: ${balance.reserved_usd}"
            )
            
            return {
                'success': True,
                'amount_held': amount_usd,
                'available_balance': balance.amount_usd,
                'reserved_balance': balance.reserved_usd,
                'transaction_id': str(transaction_record.id),
                'balance_obj': balance
            }
    
    def release_funds(
        self,
        user,
        amount_usd: Decimal,
        description: str,
        reference_id: Optional[str] = None,
        refund_to_available: bool = True
    ) -> Dict[str, Any]:
        """
        Release held funds.
        
        Args:
            user: User object
            amount_usd: Amount to release
            description: Release description
            reference_id: Optional reference ID
            refund_to_available: If True, move to available; if False, remove entirely
            
        Returns:
            Dict with operation result
        """
        if amount_usd <= 0:
            raise ValueError("Amount must be positive")
        
        with transaction.atomic():
            # Get balance with row lock
            balance = self.select_for_update().get_or_create_balance(user)
            
            # Check sufficient reserved funds
            if balance.reserved_usd < amount_usd:
                raise ValueError(
                    f"Insufficient reserved funds: ${balance.reserved_usd} < ${amount_usd}"
                )
            
            # Store old values
            old_available = balance.amount_usd
            old_reserved = balance.reserved_usd
            
            # Release funds
            balance.reserved_usd -= amount_usd
            if refund_to_available:
                balance.amount_usd += amount_usd
            else:
                # Funds are consumed (e.g., for payment)
                balance.total_spent += amount_usd
            
            balance.last_transaction_at = timezone.now()
            balance.save()
            
            # Create transaction record
            from ..models.balance import Transaction
            transaction_record = Transaction.objects.create(
                user=user,
                amount_usd=amount_usd if refund_to_available else -amount_usd,
                transaction_type=Transaction.TypeChoices.RELEASE,
                description=description,
                reference_id=reference_id,
                balance_before=old_available,
                balance_after=balance.amount_usd,
                metadata={
                    'reserved_before': str(old_reserved),
                    'reserved_after': str(balance.reserved_usd),
                    'refund_to_available': refund_to_available,
                    'operation': 'release_funds',
                }
            )
            
            action = "refunded to available" if refund_to_available else "consumed"
            logger.info(
                f"Released ${amount_usd} for user {user.id} ({action}). "
                f"Available: ${balance.amount_usd}, Reserved: ${balance.reserved_usd}"
            )
            
            return {
                'success': True,
                'amount_released': amount_usd,
                'refund_to_available': refund_to_available,
                'available_balance': balance.amount_usd,
                'reserved_balance': balance.reserved_usd,
                'transaction_id': str(transaction_record.id),
                'balance_obj': balance
            }
    
    def get_balance_summary(self, user) -> Dict[str, Any]:
        """Get comprehensive balance summary for user."""
        balance = self.get_or_create_balance(user)
        
        return {
            'user_id': user.id,
            'available_balance': balance.amount_usd,
            'reserved_balance': balance.reserved_usd,
            'total_balance': balance.total_balance,
            'total_earned': balance.total_earned,
            'total_spent': balance.total_spent,
            'last_transaction_at': balance.last_transaction_at,
            'created_at': balance.created_at,
            'updated_at': balance.updated_at,
        }
