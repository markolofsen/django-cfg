"""
Balance and transaction managers for Payments v2.0.

Optimized querysets and managers for balance and transaction operations.
"""

from decimal import Decimal

from django.db import models, transaction
from django.utils import timezone

import logging

logger = logging.getLogger(__name__)


class UserBalanceManager(models.Manager):
    """
    Manager for UserBalance operations.

    Provides methods for balance management and atomic operations.
    """

    def get_or_create_for_user(self, user):
        """
        Get or create balance for user.

        Args:
            user: User instance

        Returns:
            UserBalance: Balance instance
        """
        balance, created = self.get_or_create(
            user=user,
            defaults={
                'balance_usd': Decimal('0.00'),
                'total_deposited': Decimal('0.00'),
                'total_withdrawn': Decimal('0.00')
            }
        )

        if created:
            logger.info("Created new balance for user", extra={
                'user_id': user.id,
                'initial_balance': '0.00'
            })

        return balance

    @transaction.atomic
    def add_funds_to_user(self, user, amount, transaction_type='deposit',
                         description=None, payment_id=None):
        """
        Add funds to user balance atomically (business logic in manager).

        Args:
            user: User instance
            amount: Amount to add (positive Decimal)
            transaction_type: Type of transaction (default: 'deposit')
            description: Transaction description
            payment_id: Related payment ID (UUID)

        Returns:
            Transaction: Created transaction record

        Raises:
            ValueError: If amount is not positive
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")

        # Get or create balance
        balance = self.get_or_create_for_user(user)

        # Update balance
        balance.balance_usd += amount
        balance.total_deposited += amount
        balance.last_transaction_at = timezone.now()
        balance.save(update_fields=[
            'balance_usd', 'total_deposited', 'last_transaction_at', 'updated_at'
        ])

        # Create transaction record
        from ..balance import Transaction
        transaction_record = Transaction.objects.create(
            user=user,
            transaction_type=transaction_type,
            amount_usd=amount,
            balance_after=balance.balance_usd,
            description=description or f"Added ${amount:.2f} to balance",
            payment_id=payment_id
        )

        logger.info("Added funds to user balance", extra={
            'user_id': user.id,
            'amount': str(amount),
            'new_balance': str(balance.balance_usd),
            'transaction_id': str(transaction_record.id),
            'payment_id': str(payment_id) if payment_id else None
        })

        return transaction_record

    @transaction.atomic
    def subtract_funds_from_user(self, user, amount, transaction_type='withdrawal',
                                description=None, withdrawal_request_id=None):
        """
        Subtract funds from user balance atomically (business logic in manager).

        Args:
            user: User instance
            amount: Amount to subtract (positive Decimal)
            transaction_type: Type of transaction (default: 'withdrawal')
            description: Transaction description
            withdrawal_request_id: Related withdrawal request ID (UUID)

        Returns:
            Transaction: Created transaction record

        Raises:
            ValueError: If amount is not positive or insufficient balance
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")

        # Get balance
        try:
            balance = self.get(user=user)
        except self.model.DoesNotExist:
            raise ValueError("User has no balance record")

        if amount > balance.balance_usd:
            raise ValueError(
                f"Insufficient balance: ${balance.balance_usd:.2f} < ${amount:.2f}"
            )

        # Update balance
        balance.balance_usd -= amount
        balance.total_withdrawn += amount
        balance.last_transaction_at = timezone.now()
        balance.save(update_fields=[
            'balance_usd', 'total_withdrawn', 'last_transaction_at', 'updated_at'
        ])

        # Create transaction record
        from ..balance import Transaction
        transaction_record = Transaction.objects.create(
            user=user,
            transaction_type=transaction_type,
            amount_usd=-amount,  # Negative for withdrawals
            balance_after=balance.balance_usd,
            description=description or f"Subtracted ${amount:.2f} from balance",
            withdrawal_request_id=withdrawal_request_id
        )

        logger.info("Subtracted funds from user balance", extra={
            'user_id': user.id,
            'amount': str(amount),
            'new_balance': str(balance.balance_usd),
            'transaction_id': str(transaction_record.id),
            'withdrawal_request_id': str(withdrawal_request_id) if withdrawal_request_id else None
        })

        return transaction_record


class TransactionQuerySet(models.QuerySet):
    """
    Optimized queryset for transaction operations.

    Provides efficient queries for transaction history and analysis.
    """

    def optimized(self):
        """Prevent N+1 queries with select_related."""
        return self.select_related('user')

    def by_user(self, user):
        """Filter transactions by user."""
        return self.filter(user=user)

    def by_type(self, transaction_type):
        """Filter by transaction type."""
        return self.filter(transaction_type=transaction_type)

    def by_payment(self, payment_id):
        """Filter by related payment ID."""
        return self.filter(payment_id=payment_id)

    def by_withdrawal_request(self, withdrawal_request_id):
        """Filter by related withdrawal request ID."""
        return self.filter(withdrawal_request_id=withdrawal_request_id)

    # Transaction type filters
    def deposits(self):
        """Get deposit transactions (positive amounts)."""
        return self.filter(transaction_type='deposit', amount_usd__gt=0)

    def withdrawals(self):
        """Get withdrawal transactions (negative amounts)."""
        return self.filter(transaction_type='withdrawal', amount_usd__lt=0)

    # Amount-based filters
    def credits(self):
        """Get credit transactions (positive amounts)."""
        return self.filter(amount_usd__gt=0)

    def debits(self):
        """Get debit transactions (negative amounts)."""
        return self.filter(amount_usd__lt=0)

    def large_amounts(self, threshold=100.0):
        """
        Get transactions above threshold amount.

        Args:
            threshold: USD amount threshold (default: $100)
        """
        return self.filter(models.Q(amount_usd__gte=threshold) | models.Q(amount_usd__lte=-threshold))

    def small_amounts(self, threshold=10.0):
        """
        Get transactions below threshold amount.

        Args:
            threshold: USD amount threshold (default: $10)
        """
        return self.filter(
            amount_usd__gt=-threshold,
            amount_usd__lt=threshold
        ).exclude(amount_usd=0)

    # Time-based filters
    def recent(self, hours=24):
        """
        Get transactions from last N hours.

        Args:
            hours: Number of hours to look back (default: 24)
        """
        since = timezone.now() - timezone.timedelta(hours=hours)
        return self.filter(created_at__gte=since)

    def today(self):
        """Get transactions created today."""
        today = timezone.now().date()
        return self.filter(created_at__date=today)

    def this_week(self):
        """Get transactions from this week."""
        week_start = timezone.now().date() - timezone.timedelta(days=timezone.now().weekday())
        return self.filter(created_at__date__gte=week_start)

    def this_month(self):
        """Get transactions from this month."""
        month_start = timezone.now().replace(day=1).date()
        return self.filter(created_at__date__gte=month_start)

    def date_range(self, start_date, end_date):
        """
        Get transactions within date range.

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
        """
        return self.filter(created_at__date__range=[start_date, end_date])

    # Aggregation methods
    def total_amount(self):
        """Get total amount for queryset."""
        result = self.aggregate(total=models.Sum('amount_usd'))
        return result['total'] or Decimal('0.00')

    def total_credits(self):
        """Get total credit amount."""
        result = self.credits().aggregate(total=models.Sum('amount_usd'))
        return result['total'] or Decimal('0.00')

    def total_debits(self):
        """Get total debit amount (absolute value)."""
        result = self.debits().aggregate(total=models.Sum('amount_usd'))
        return abs(result['total'] or Decimal('0.00'))

    def average_amount(self):
        """Get average transaction amount."""
        result = self.aggregate(avg=models.Avg('amount_usd'))
        return result['avg'] or Decimal('0.00')

    def count_by_type(self):
        """Get count of transactions grouped by type."""
        return self.values('transaction_type').annotate(
            count=models.Count('id'),
            total_amount=models.Sum('amount_usd')
        ).order_by('transaction_type')


class TransactionManager(models.Manager):
    """
    Manager for transaction operations with optimized queries.

    Provides high-level methods for transaction analysis and reporting.
    """

    def get_queryset(self):
        """Return optimized queryset by default."""
        return TransactionQuerySet(self.model, using=self._db)

    def optimized(self):
        """Get optimized queryset."""
        return self.get_queryset().optimized()

    # User-based methods
    def by_user(self, user):
        """Get transactions by user."""
        return self.get_queryset().by_user(user)

    def by_type(self, transaction_type):
        """Get transactions by type."""
        return self.get_queryset().by_type(transaction_type)

    # Transaction type methods
    def deposits(self):
        """Get deposit transactions."""
        return self.get_queryset().deposits()

    def withdrawals(self):
        """Get withdrawal transactions."""
        return self.get_queryset().withdrawals()

    def credits(self):
        """Get credit transactions (positive amounts)."""
        return self.get_queryset().credits()

    def debits(self):
        """Get debit transactions (negative amounts)."""
        return self.get_queryset().debits()

    # Time-based methods
    def recent(self, hours=24):
        """Get recent transactions."""
        return self.get_queryset().recent(hours)

    def today(self):
        """Get today's transactions."""
        return self.get_queryset().today()

    def this_week(self):
        """Get this week's transactions."""
        return self.get_queryset().this_week()

    def this_month(self):
        """Get this month's transactions."""
        return self.get_queryset().this_month()

    # Analysis methods
    def get_user_balance_history(self, user, days=30):
        """
        Get balance history for a user over the last N days.

        Args:
            user: User instance
            days: Number of days to analyze (default: 30)

        Returns:
            list: Daily balance snapshots
        """
        transactions = self.by_user(user).filter(
            created_at__gte=timezone.now() - timezone.timedelta(days=days)
        ).order_by('created_at')

        history = []
        for txn in transactions:
            history.append({
                'date': txn.created_at.date(),
                'balance': str(txn.balance_after),
                'transaction_id': str(txn.id),
                'transaction_type': txn.transaction_type,
                'amount': str(txn.amount_usd)
            })

        return history

    def get_transaction_stats(self, user=None, days=30):
        """
        Get transaction statistics.

        Args:
            user: User instance (optional, for user-specific stats)
            days: Number of days to analyze (default: 30)

        Returns:
            dict: Transaction statistics
        """
        queryset = self.get_queryset()
        if user:
            queryset = queryset.by_user(user)

        since = timezone.now() - timezone.timedelta(days=days)
        queryset = queryset.filter(created_at__gte=since)

        stats = {
            'total_transactions': queryset.count(),
            'total_amount': str(queryset.total_amount()),
            'total_credits': str(queryset.total_credits()),
            'total_debits': str(queryset.total_debits()),
            'average_amount': str(queryset.average_amount()),
            'by_type': list(queryset.count_by_type()),
            'deposits_count': queryset.deposits().count(),
            'withdrawals_count': queryset.withdrawals().count(),
        }

        logger.info(f"Generated transaction stats for {days} days", extra={
            'user_id': user.id if user else None,
            'days': days,
            'total_transactions': stats['total_transactions'],
            'total_amount': stats['total_amount']
        })

        return stats
