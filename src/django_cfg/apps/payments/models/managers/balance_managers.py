"""
Balance and transaction managers for the Universal Payment System v2.0.

Optimized querysets and managers for balance and transaction operations.
"""

from django.db import models, transaction
from django.utils import timezone
from django_cfg.modules.django_logger import get_logger

logger = get_logger("balance_managers")


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
            defaults={'balance_usd': 0.0}
        )
        
        if created:
            logger.info(f"Created new balance for user", extra={
                'user_id': user.id,
                'initial_balance': 0.0
            })
        
        return balance
    
    def add_funds_to_user(self, user, amount, transaction_type='deposit', 
                         description=None, payment_id=None):
        """
        Add funds to user balance atomically (business logic in manager).
        
        Args:
            user: User instance
            amount: Amount to add (positive)
            transaction_type: Type of transaction
            description: Transaction description
            payment_id: Related payment ID
        
        Returns:
            Transaction: Created transaction record
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        # Get or create balance
        balance = self.get_or_create_for_user(user)
        
        with transaction.atomic():
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
            
            logger.info(f"Added funds to user balance", extra={
                'user_id': user.id,
                'amount': amount,
                'new_balance': balance.balance_usd,
                'transaction_id': str(transaction_record.id),
                'payment_id': payment_id
            })
            
            # Update analytics
            self.update_balance_analytics(user, amount)
            
            return transaction_record
    
    def subtract_funds_from_user(self, user, amount, transaction_type='withdrawal',
                                description=None, payment_id=None):
        """
        Subtract funds from user balance atomically (business logic in manager).
        
        Args:
            user: User instance
            amount: Amount to subtract (positive)
            transaction_type: Type of transaction
            description: Transaction description
            payment_id: Related payment ID
        
        Returns:
            Transaction: Created transaction record
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        # Get balance
        try:
            balance = self.get(user=user)
        except self.model.DoesNotExist:
            raise ValueError("User has no balance record")
        
        if amount > balance.balance_usd:
            raise ValueError(f"Insufficient balance: ${balance.balance_usd:.2f} < ${amount:.2f}")
        
        with transaction.atomic():
            # Update balance
            balance.balance_usd -= amount
            balance.total_spent += amount
            balance.last_transaction_at = timezone.now()
            balance.save(update_fields=[
                'balance_usd', 'total_spent', 'last_transaction_at', 'updated_at'
            ])
            
            # Create transaction record
            from ..balance import Transaction
            transaction_record = Transaction.objects.create(
                user=user,
                transaction_type=transaction_type,
                amount_usd=-amount,  # Negative for withdrawals
                balance_after=balance.balance_usd,
                description=description or f"Subtracted ${amount:.2f} from balance",
                payment_id=payment_id
            )
            
        logger.info(f"Subtracted funds from user balance", extra={
            'user_id': user.id,
            'amount': amount,
            'new_balance': balance.balance_usd,
            'transaction_id': str(transaction_record.id),
            'payment_id': payment_id
        })
        
        # Update analytics
        self.update_balance_analytics(user, -amount)
        
        return transaction_record
    
    def update_balance_analytics(self, user, balance_change):
        """
        Update balance analytics in cache (moved from signals).
        
        Args:
            user: User instance
            balance_change: Amount of balance change
        """
        try:
            from django.core.cache import cache
            
            user_id = user.id
            
            # Update balance history
            history_key = f"balance_history:{user_id}"
            history = cache.get(history_key, [])
            
            history.append({
                'timestamp': timezone.now().isoformat(),
                'balance': self.get_or_create_for_user(user).balance_usd,
                'change': balance_change
            })
            
            # Keep only last 100 entries
            if len(history) > 100:
                history = history[-100:]
            
            cache.set(history_key, history, timeout=86400 * 7)  # 7 days
            
            # Update daily totals
            today = timezone.now().date().isoformat()
            daily_key = f"balance_changes:{user_id}:{today}"
            
            daily_data = cache.get(daily_key, {'total_change': 0.0, 'transaction_count': 0})
            daily_data['total_change'] += balance_change
            daily_data['transaction_count'] += 1
            
            cache.set(daily_key, daily_data, timeout=86400 * 2)  # 2 days
            
            logger.debug(f"Updated balance analytics", extra={
                'user_id': user_id,
                'balance_change': balance_change,
                'total_change_today': daily_data['total_change']
            })
            
        except Exception as e:
            logger.warning(f"Failed to update balance analytics", extra={
                'user_id': user.id,
                'error': str(e)
            })


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
    
    # Transaction type filters
    def deposits(self):
        """Get deposit transactions (positive amounts)."""
        return self.filter(transaction_type='deposit', amount_usd__gt=0)
    
    def withdrawals(self):
        """Get withdrawal transactions (negative amounts)."""
        return self.filter(transaction_type='withdrawal', amount_usd__lt=0)
    
    def payments(self):
        """Get payment-related transactions."""
        return self.filter(transaction_type='payment')
    
    def refunds(self):
        """Get refund transactions."""
        return self.filter(transaction_type='refund')
    
    def fees(self):
        """Get fee transactions."""
        return self.filter(transaction_type='fee')
    
    def bonuses(self):
        """Get bonus transactions."""
        return self.filter(transaction_type='bonus')
    
    def adjustments(self):
        """Get adjustment transactions."""
        return self.filter(transaction_type='adjustment')
    
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
        return self.filter(amount_usd__gte=threshold)
    
    def small_amounts(self, threshold=10.0):
        """
        Get transactions below threshold amount.
        
        Args:
            threshold: USD amount threshold (default: $10)
        """
        return self.filter(amount_usd__lte=threshold)
    
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
        return result['total'] or 0.0
    
    def total_credits(self):
        """Get total credit amount."""
        result = self.credits().aggregate(total=models.Sum('amount_usd'))
        return result['total'] or 0.0
    
    def total_debits(self):
        """Get total debit amount (absolute value)."""
        result = self.debits().aggregate(total=models.Sum('amount_usd'))
        return abs(result['total'] or 0.0)
    
    def average_amount(self):
        """Get average transaction amount."""
        result = self.aggregate(avg=models.Avg('amount_usd'))
        return result['avg'] or 0.0
    
    def count_by_type(self):
        """Get count of transactions grouped by type."""
        return self.values('transaction_type').annotate(
            count=models.Count('id'),
            total_amount=models.Sum('amount_usd')
        ).order_by('transaction_type')
    
    def daily_summary(self, days=30):
        """
        Get daily transaction summary for the last N days.
        
        Args:
            days: Number of days to analyze (default: 30)
        """
        since = timezone.now().date() - timezone.timedelta(days=days)
        return self.filter(created_at__date__gte=since).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(
            count=models.Count('id'),
            total_amount=models.Sum('amount_usd'),
            credits=models.Sum('amount_usd', filter=models.Q(amount_usd__gt=0)),
            debits=models.Sum('amount_usd', filter=models.Q(amount_usd__lt=0))
        ).order_by('day')


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
    
    def payments(self):
        """Get payment transactions."""
        return self.get_queryset().payments()
    
    def refunds(self):
        """Get refund transactions."""
        return self.get_queryset().refunds()
    
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
        current_balance = 0.0
        
        for transaction in transactions:
            current_balance = transaction.balance_after
            history.append({
                'date': transaction.created_at.date(),
                'balance': current_balance,
                'transaction_id': str(transaction.id),
                'transaction_type': transaction.transaction_type,
                'amount': transaction.amount_usd
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
            'total_amount': queryset.total_amount(),
            'total_credits': queryset.total_credits(),
            'total_debits': queryset.total_debits(),
            'average_amount': queryset.average_amount(),
            'by_type': list(queryset.count_by_type()),
            'deposits_count': queryset.deposits().count(),
            'withdrawals_count': queryset.withdrawals().count(),
            'payments_count': queryset.payments().count(),
            'refunds_count': queryset.refunds().count(),
        }
        
        logger.info(f"Generated transaction stats for {days} days", extra={
            'user_id': user.id if user else None,
            'days': days,
            'total_transactions': stats['total_transactions'],
            'total_amount': stats['total_amount']
        })
        
        return stats
    
    def get_daily_summary(self, days=30):
        """
        Get daily transaction summary.
        
        Args:
            days: Number of days to analyze (default: 30)
        
        Returns:
            QuerySet: Daily summary data
        """
        return self.get_queryset().daily_summary(days)
    
    def create_deposit(self, user, amount, description=None, payment_id=None, metadata=None):
        """
        Create a deposit transaction.
        
        Args:
            user: User instance
            amount: Deposit amount (positive)
            description: Transaction description
            payment_id: Related payment ID
            metadata: Additional metadata
        
        Returns:
            Transaction: Created transaction
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        # Get or create user balance
        from ..balance import UserBalance
        balance = UserBalance.get_or_create_for_user(user)
        
        # Create transaction via balance method (ensures atomicity)
        transaction = balance.add_funds(
            amount=amount,
            transaction_type='deposit',
            description=description or f"Deposit of ${amount:.2f}",
            payment_id=payment_id
        )
        
        # Add metadata if provided
        if metadata:
            transaction.metadata = metadata
            transaction.save(update_fields=['metadata'])
        
        logger.info(f"Created deposit transaction", extra={
            'user_id': user.id,
            'amount': amount,
            'transaction_id': str(transaction.id),
            'payment_id': payment_id
        })
        
        return transaction
    
    def create_withdrawal(self, user, amount, description=None, payment_id=None, metadata=None):
        """
        Create a withdrawal transaction.
        
        Args:
            user: User instance
            amount: Withdrawal amount (positive, will be made negative)
            description: Transaction description
            payment_id: Related payment ID
            metadata: Additional metadata
        
        Returns:
            Transaction: Created transaction
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        
        # Get user balance
        from ..balance import UserBalance
        try:
            balance = UserBalance.objects.get(user=user)
        except UserBalance.DoesNotExist:
            raise ValueError("User has no balance record")
        
        # Create transaction via balance method (ensures atomicity)
        transaction = balance.subtract_funds(
            amount=amount,
            transaction_type='withdrawal',
            description=description or f"Withdrawal of ${amount:.2f}",
            payment_id=payment_id
        )
        
        # Add metadata if provided
        if metadata:
            transaction.metadata = metadata
            transaction.save(update_fields=['metadata'])
        
        logger.info(f"Created withdrawal transaction", extra={
            'user_id': user.id,
            'amount': amount,
            'transaction_id': str(transaction.id),
            'payment_id': payment_id
        })
        
        return transaction
