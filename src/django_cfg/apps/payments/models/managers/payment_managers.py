"""
Payment managers for the Universal Payment System v2.0.

Optimized querysets and managers for payment operations.
"""

from django.db import models
from django.utils import timezone
from django_cfg.modules.django_logger import get_logger

logger = get_logger("payment_managers")


class PaymentQuerySet(models.QuerySet):
    """
    Optimized queryset for payment operations.
    
    Provides efficient queries with proper indexing and select_related optimization.
    """
    
    def optimized(self):
        """
        Prevent N+1 queries with select_related and prefetch_related.
        
        Use this for admin interfaces and API responses.
        """
        return self.select_related(
            'user', 
            'currency', 
            'network'
        ).prefetch_related(
            'user__payment_balance',
            'user__payment_transactions'
        )
    
    def by_status(self, status):
        """Filter by payment status with index optimization."""
        return self.filter(status=status)
    
    def by_provider(self, provider):
        """Filter by payment provider."""
        return self.filter(provider=provider)
    
    def by_user(self, user):
        """Filter by user with proper indexing."""
        return self.filter(user=user)
    
    def by_amount_range(self, min_amount=None, max_amount=None):
        """
        Filter by USD amount range.
        
        Args:
            min_amount: Minimum amount in USD (inclusive)
            max_amount: Maximum amount in USD (inclusive)
        """
        queryset = self
        if min_amount is not None:
            queryset = queryset.filter(amount_usd__gte=min_amount)
        if max_amount is not None:
            queryset = queryset.filter(amount_usd__lte=max_amount)
        return queryset
    
    def by_currency(self, currency_code):
        """Filter by currency code."""
        return self.filter(currency__code=currency_code)
    
    def by_network(self, network_code):
        """Filter by blockchain network."""
        return self.filter(network__code=network_code)
    
    # Status-based filters
    def completed(self):
        """Get completed payments."""
        return self.filter(status='completed')
    
    def pending(self):
        """Get pending payments."""
        return self.filter(status='pending')
    
    def failed(self):
        """Get failed payments (failed, expired, cancelled)."""
        return self.filter(status__in=['failed', 'expired', 'cancelled'])
    
    def confirming(self):
        """Get payments awaiting confirmation."""
        return self.filter(status__in=['confirming', 'confirmed'])
    
    def active(self):
        """Get active payments (not failed or completed)."""
        return self.filter(status__in=['pending', 'confirming', 'confirmed'])
    
    # Time-based filters
    def recent(self, hours=24):
        """
        Get payments from last N hours.
        
        Args:
            hours: Number of hours to look back (default: 24)
        """
        since = timezone.now() - timezone.timedelta(hours=hours)
        return self.filter(created_at__gte=since)
    
    def today(self):
        """Get payments created today."""
        today = timezone.now().date()
        return self.filter(created_at__date=today)
    
    def this_week(self):
        """Get payments from this week."""
        week_start = timezone.now().date() - timezone.timedelta(days=timezone.now().weekday())
        return self.filter(created_at__date__gte=week_start)
    
    def this_month(self):
        """Get payments from this month."""
        month_start = timezone.now().replace(day=1).date()
        return self.filter(created_at__date__gte=month_start)
    
    def expired(self):
        """Get expired payments."""
        now = timezone.now()
        return self.filter(
            expires_at__lte=now,
            status__in=['pending', 'confirming']
        )
    
    def expiring_soon(self, hours=2):
        """
        Get payments expiring in the next N hours.
        
        Args:
            hours: Hours until expiration (default: 2)
        """
        soon = timezone.now() + timezone.timedelta(hours=hours)
        return self.filter(
            expires_at__lte=soon,
            expires_at__gt=timezone.now(),
            status__in=['pending', 'confirming']
        )
    
    # Provider-specific filters
    def nowpayments(self):
        """Get NowPayments payments."""
        return self.filter(provider='nowpayments')
    
    def crypto_payments(self):
        """Get cryptocurrency payments."""
        return self.filter(currency__currency_type='crypto')
    
    def fiat_payments(self):
        """Get fiat currency payments."""
        return self.filter(currency__currency_type='fiat')
    
    # Aggregation methods
    def total_amount(self):
        """Get total USD amount for queryset."""
        result = self.aggregate(total=models.Sum('amount_usd'))
        return result['total'] or 0.0
    
    def average_amount(self):
        """Get average USD amount for queryset."""
        result = self.aggregate(avg=models.Avg('amount_usd'))
        return result['avg'] or 0.0
    
    def count_by_status(self):
        """Get count of payments grouped by status."""
        return self.values('status').annotate(count=models.Count('id')).order_by('status')
    
    def count_by_provider(self):
        """Get count of payments grouped by provider."""
        return self.values('provider').annotate(count=models.Count('id')).order_by('provider')
    
    def count_by_currency(self):
        """Get count of payments grouped by currency."""
        return self.values('currency__code').annotate(count=models.Count('id')).order_by('currency__code')
    
    # Advanced queries
    def with_transactions(self):
        """Include related transaction data."""
        return self.prefetch_related('user__payment_transactions')
    
    def with_balance_info(self):
        """Include user balance information."""
        return self.select_related('user__payment_balance')
    
    def requiring_confirmation(self):
        """Get payments that need blockchain confirmation."""
        return self.filter(
            status__in=['confirming', 'confirmed'],
            transaction_hash__isnull=False
        )
    
    def large_amounts(self, threshold=1000.0):
        """
        Get payments above threshold amount.
        
        Args:
            threshold: USD amount threshold (default: $1000)
        """
        return self.filter(amount_usd__gte=threshold)
    
    def small_amounts(self, threshold=10.0):
        """
        Get payments below threshold amount.
        
        Args:
            threshold: USD amount threshold (default: $10)
        """
        return self.filter(amount_usd__lte=threshold)


class PaymentManager(models.Manager):
    """
    Manager for payment operations with optimized queries.
    
    Provides high-level methods for common payment operations.
    """
    
    def get_queryset(self):
        """Return optimized queryset by default."""
        return PaymentQuerySet(self.model, using=self._db)
    
    def optimized(self):
        """Get optimized queryset for admin/API use."""
        return self.get_queryset().optimized()
    
    # Status-based methods
    def by_status(self, status):
        """Get payments by status."""
        return self.get_queryset().by_status(status)
    
    def completed(self):
        """Get completed payments."""
        return self.get_queryset().completed()
    
    def pending(self):
        """Get pending payments."""
        return self.get_queryset().pending()
    
    def failed(self):
        """Get failed payments."""
        return self.get_queryset().failed()
    
    def active(self):
        """Get active payments."""
        return self.get_queryset().active()
    
    # User-based methods
    def by_user(self, user):
        """Get payments by user."""
        return self.get_queryset().by_user(user)
    
    # Provider-based methods
    def by_provider(self, provider):
        """Get payments by provider."""
        return self.get_queryset().by_provider(provider)
    
    def nowpayments(self):
        """Get NowPayments payments."""
        return self.get_queryset().nowpayments()
    
    # Time-based methods
    def recent(self, hours=24):
        """Get recent payments."""
        return self.get_queryset().recent(hours)
    
    def today(self):
        """Get today's payments."""
        return self.get_queryset().today()
    
    def this_week(self):
        """Get this week's payments."""
        return self.get_queryset().this_week()
    
    def this_month(self):
        """Get this month's payments."""
        return self.get_queryset().this_month()
    
    # Maintenance methods
    def expired(self):
        """Get expired payments."""
        return self.get_queryset().expired()
    
    def expiring_soon(self, hours=2):
        """Get payments expiring soon."""
        return self.get_queryset().expiring_soon(hours)
    
    def requiring_confirmation(self):
        """Get payments needing confirmation."""
        return self.get_queryset().requiring_confirmation()
    
    # Statistics methods
    def get_stats(self, days=30):
        """
        Get payment statistics for the last N days.
        
        Args:
            days: Number of days to analyze (default: 30)
        
        Returns:
            dict: Statistics including totals, averages, and counts
        """
        since = timezone.now() - timezone.timedelta(days=days)
        queryset = self.filter(created_at__gte=since)
        
        stats = {
            'total_payments': queryset.count(),
            'total_amount_usd': queryset.total_amount(),
            'average_amount_usd': queryset.average_amount(),
            'completed_payments': queryset.completed().count(),
            'pending_payments': queryset.pending().count(),
            'failed_payments': queryset.failed().count(),
            'by_status': list(queryset.count_by_status()),
            'by_provider': list(queryset.count_by_provider()),
            'by_currency': list(queryset.count_by_currency()),
        }
        
        logger.info(f"Generated payment stats for {days} days", extra={
            'days': days,
            'total_payments': stats['total_payments'],
            'total_amount': stats['total_amount_usd']
        })
        
        return stats
    
    def cleanup_expired(self, dry_run=True):
        """
        Mark expired payments as failed.
        
        Args:
            dry_run: If True, only return count without making changes
        
        Returns:
            int: Number of payments that would be/were updated
        """
        expired_payments = self.expired()
        count = expired_payments.count()
        
        if not dry_run and count > 0:
            expired_payments.update(status='expired')
            logger.info(f"Marked {count} payments as expired")
        
        return count
    
    def get_user_payment_summary(self, user):
        """
        Get payment summary for a specific user.
        
        Args:
            user: User instance
        
        Returns:
            dict: User payment summary
        """
        user_payments = self.filter(user=user)
        
        summary = {
            'total_payments': user_payments.count(),
            'total_amount_usd': user_payments.total_amount(),
            'completed_payments': user_payments.completed().count(),
            'pending_payments': user_payments.pending().count(),
            'failed_payments': user_payments.failed().count(),
            'last_payment_at': user_payments.first().created_at if user_payments.exists() else None,
            'average_amount_usd': user_payments.average_amount(),
        }
        
        return summary
    
    # Business logic methods
    def mark_payment_completed(self, payment_id, actual_amount_usd=None, transaction_hash=None):
        """
        Mark payment as completed (business logic in manager).
        
        Args:
            payment_id: Payment ID or instance
            actual_amount_usd: Actual amount received
            transaction_hash: Blockchain transaction hash
        
        Returns:
            bool: True if payment was updated successfully
        """
        try:
            if isinstance(payment_id, str):
                payment = self.get(id=payment_id)
            else:
                payment = payment_id
            
            # Validate payment can be completed
            if not payment.status in ['pending', 'confirming', 'confirmed']:
                logger.warning(f"Cannot complete payment in status {payment.status}", extra={
                    'payment_id': str(payment.id),
                    'current_status': payment.status
                })
                return False
            
            # Update payment
            payment.status = 'completed'
            payment.completed_at = timezone.now()
            if actual_amount_usd:
                payment.actual_amount_usd = actual_amount_usd
            if transaction_hash:
                payment.transaction_hash = transaction_hash
            
            payment.save(update_fields=[
                'status', 'completed_at', 'actual_amount_usd', 'transaction_hash', 'updated_at'
            ])
            
            logger.info(f"Payment marked as completed", extra={
                'payment_id': str(payment.id),
                'user_id': payment.user.id,
                'amount_usd': payment.amount_usd,
                'actual_amount_usd': actual_amount_usd,
                'transaction_hash': transaction_hash
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark payment as completed: {e}", extra={
                'payment_id': str(payment_id) if hasattr(payment_id, 'id') else payment_id
            })
            return False
    
    def mark_payment_failed(self, payment_id, reason=None, error_code=None):
        """
        Mark payment as failed (business logic in manager).
        
        Args:
            payment_id: Payment ID or instance
            reason: Failure reason
            error_code: Error code for categorization
        
        Returns:
            bool: True if payment was updated successfully
        """
        try:
            if isinstance(payment_id, str):
                payment = self.get(id=payment_id)
            else:
                payment = payment_id
            
            # Update payment
            payment.status = 'failed'
            if reason or error_code:
                if 'error_info' not in payment.provider_data:
                    payment.provider_data['error_info'] = {}
                if reason:
                    payment.provider_data['error_info']['reason'] = reason
                if error_code:
                    payment.provider_data['error_info']['code'] = error_code
                payment.provider_data['error_info']['failed_at'] = timezone.now().isoformat()
            
            payment.save(update_fields=['status', 'provider_data', 'updated_at'])
            
            logger.warning(f"Payment marked as failed", extra={
                'payment_id': str(payment.id),
                'user_id': payment.user.id,
                'reason': reason,
                'error_code': error_code
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark payment as failed: {e}", extra={
                'payment_id': str(payment_id) if hasattr(payment_id, 'id') else payment_id
            })
            return False
    
    def cancel_payment(self, payment_id, reason=None):
        """
        Cancel payment (business logic in manager).
        
        Args:
            payment_id: Payment ID or instance
            reason: Cancellation reason
        
        Returns:
            bool: True if payment was cancelled successfully
        """
        try:
            if isinstance(payment_id, str):
                payment = self.get(id=payment_id)
            else:
                payment = payment_id
            
            # Validate payment can be cancelled
            if not payment.status in ['pending', 'confirming']:
                logger.warning(f"Cannot cancel payment in status {payment.status}", extra={
                    'payment_id': str(payment.id),
                    'current_status': payment.status
                })
                return False
            
            # Update payment
            payment.status = 'cancelled'
            if reason:
                if 'cancellation_info' not in payment.provider_data:
                    payment.provider_data['cancellation_info'] = {}
                payment.provider_data['cancellation_info']['reason'] = reason
                payment.provider_data['cancellation_info']['cancelled_at'] = timezone.now().isoformat()
            
            payment.save(update_fields=['status', 'provider_data', 'updated_at'])
            
            logger.info(f"Payment cancelled", extra={
                'payment_id': str(payment.id),
                'user_id': payment.user.id,
                'reason': reason
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel payment: {e}", extra={
                'payment_id': str(payment_id) if hasattr(payment_id, 'id') else payment_id
            })
            return False
