"""
Balance service for Payments v2.0.

Service layer for balance and transaction operations.
"""

import logging
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from django.contrib.auth import get_user_model
from pydantic import BaseModel, ConfigDict, Field

from ..models import UserBalance, Transaction

User = get_user_model()
logger = logging.getLogger(__name__)


# Pydantic models

class BalanceInfo(BaseModel):
    """Balance information."""

    user_id: int
    balance_usd: Decimal
    total_deposited: Decimal
    total_withdrawn: Decimal
    last_transaction_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TransactionInfo(BaseModel):
    """Transaction information."""

    id: UUID
    transaction_type: str
    amount_usd: Decimal
    balance_after: Decimal
    payment_id: Optional[str] = None
    description: str
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class GetBalanceRequest(BaseModel):
    """Request для получения баланса."""

    user_id: int

    model_config = ConfigDict(frozen=True)


class GetTransactionsRequest(BaseModel):
    """Request для получения транзакций."""

    user_id: int
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    transaction_type: Optional[str] = None

    model_config = ConfigDict(frozen=True)


class TransactionsResult(BaseModel):
    """Result списка транзакций."""

    transactions: List[TransactionInfo]
    total_count: int
    has_more: bool


# Service class

class BalanceService:
    """
    Service для работы с балансом и транзакциями.

    ORM-based balance calculation.
    """

    def get_balance(self, request: GetBalanceRequest) -> Optional[BalanceInfo]:
        """
        Получить баланс пользователя.

        Args:
            request: Validated request

        Returns:
            BalanceInfo or None if user not found
        """
        try:
            # Get or create balance
            user = User.objects.get(id=request.user_id)
            balance = UserBalance.get_or_create_for_user(user)

            return BalanceInfo(
                user_id=balance.user_id,
                balance_usd=balance.balance_usd,
                total_deposited=balance.total_deposited,
                total_withdrawn=balance.total_withdrawn,
                last_transaction_at=balance.last_transaction_at.isoformat() if balance.last_transaction_at else None
            )

        except User.DoesNotExist:
            logger.warning(f"User not found: {request.user_id}")
            return None
        except Exception as e:
            logger.exception(f"Failed to get balance: {e}")
            return None

    def get_transactions(self, request: GetTransactionsRequest) -> TransactionsResult:
        """
        Получить список транзакций пользователя.

        Args:
            request: Validated request

        Returns:
            TransactionsResult with paginated transactions
        """
        try:
            # Build query
            queryset = Transaction.objects.filter(user_id=request.user_id)

            # Filter by type if specified
            if request.transaction_type:
                queryset = queryset.filter(transaction_type=request.transaction_type)

            # Get total count
            total_count = queryset.count()

            # Apply pagination
            transactions = queryset[request.offset:request.offset + request.limit]

            # Convert to Pydantic models
            transaction_infos = [
                TransactionInfo(
                    id=t.id,
                    transaction_type=t.transaction_type,
                    amount_usd=t.amount_usd,
                    balance_after=t.balance_after,
                    payment_id=t.payment_id,
                    description=t.description,
                    created_at=t.created_at.isoformat()
                )
                for t in transactions
            ]

            return TransactionsResult(
                transactions=transaction_infos,
                total_count=total_count,
                has_more=(request.offset + request.limit) < total_count
            )

        except Exception as e:
            logger.exception(f"Failed to get transactions: {e}")
            return TransactionsResult(
                transactions=[],
                total_count=0,
                has_more=False
            )

    def recalculate_balance(self, user_id: int) -> Optional[Decimal]:
        """
        Пересчитать баланс из транзакций (for admin/debugging).

        Args:
            user_id: User ID

        Returns:
            New balance or None if failed
        """
        try:
            user = User.objects.get(id=user_id)
            balance = UserBalance.get_or_create_for_user(user)

            # Calculate from transactions
            transactions = Transaction.objects.filter(user_id=user_id).order_by('created_at')

            calculated_balance = Decimal('0.00')
            total_deposited = Decimal('0.00')
            total_withdrawn = Decimal('0.00')

            for transaction in transactions:
                calculated_balance += transaction.amount_usd

                if transaction.transaction_type in ['deposit', 'bonus', 'refund']:
                    total_deposited += abs(transaction.amount_usd)
                elif transaction.transaction_type in ['withdrawal', 'payment', 'fee']:
                    total_withdrawn += abs(transaction.amount_usd)

            # Update balance
            balance.balance_usd = calculated_balance
            balance.total_deposited = total_deposited
            balance.total_withdrawn = total_withdrawn
            balance.save(update_fields=['balance_usd', 'total_deposited', 'total_withdrawn', 'updated_at'])

            logger.info(
                f"Balance recalculated for user {user_id}: "
                f"${calculated_balance} (deposited: ${total_deposited}, withdrawn: ${total_withdrawn})"
            )

            return calculated_balance

        except User.DoesNotExist:
            logger.error(f"User not found: {user_id}")
            return None
        except Exception as e:
            logger.exception(f"Failed to recalculate balance: {e}")
            return None
