"""
Payment managers for Payments v2.0.

Optimized querysets and managers for payment operations.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from django.db import models
from django.utils import timezone
from pydantic import BaseModel, ConfigDict, Field

import logging

logger = logging.getLogger(__name__)


class PaymentStatusUpdateFields(BaseModel):
    """
    Typed model for extra fields when updating payment status.

    Ensures type safety and validation for payment status updates.
    Uses Pydantic v2 for immutable validation.
    """
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True,
        frozen=True  # Immutable
    )

    # Transaction related fields
    transaction_hash: Optional[str] = Field(None, min_length=1, max_length=200, description="Blockchain transaction hash")
    confirmations_count: Optional[int] = Field(None, ge=0, description="Number of blockchain confirmations")

    # Amount related fields
    actual_amount_crypto: Optional[Decimal] = Field(None, gt=0, description="Actual amount received in crypto")

    # Provider data
    provider_data: Optional[Dict[str, Any]] = Field(None, description="Provider-specific data")

    # Completion timestamp (auto-set by manager for completed status)
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")


class PaymentQuerySet(models.QuerySet):
    """
    Optimized queryset for payment operations.

    Provides efficient queries with proper indexing and select_related optimization.
    """

    def optimized(self):
        """
        Prevent N+1 queries with select_related.

        Use this for admin interfaces and API responses.
        """
        return self.select_related('user', 'currency')

    def by_status(self, status):
        """Filter by payment status with index optimization."""
        return self.filter(status=status)

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
        """Filter by currency code (e.g., USDTTRC20)."""
        return self.filter(currency__code=currency_code)

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
        return self.filter(status='confirming')

    def confirmed(self):
        """Get confirmed payments (awaiting completion)."""
        return self.filter(status='confirmed')

    def partially_paid(self):
        """Get partially paid payments (95% threshold)."""
        return self.filter(status='partially_paid')

    def active(self):
        """Get active payments (not failed or completed)."""
        return self.filter(status__in=['pending', 'confirming', 'confirmed', 'partially_paid'])

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
        """Get expired payments (status check only, no expires_at field)."""
        return self.filter(status='expired')

    # Aggregation methods
    def total_amount(self):
        """Get total USD amount for queryset."""
        result = self.aggregate(total=models.Sum('amount_usd'))
        return result['total'] or Decimal('0.00')

    def average_amount(self):
        """Get average USD amount for queryset."""
        result = self.aggregate(avg=models.Avg('amount_usd'))
        return result['avg'] or Decimal('0.00')

    def count_by_status(self):
        """Get count of payments grouped by status."""
        return self.values('status').annotate(count=models.Count('id')).order_by('status')

    def count_by_currency(self):
        """Get count of payments grouped by currency."""
        return self.values('currency__code').annotate(count=models.Count('id')).order_by('currency__code')

    # Advanced queries
    def with_transactions(self):
        """Include related transaction data."""
        return self.prefetch_related('transaction_set')

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

    def partially_paid(self):
        """Get partially paid payments."""
        return self.get_queryset().partially_paid()

    # Aggregation methods
    def count_by_status(self):
        """Get count of payments grouped by status."""
        return self.get_queryset().count_by_status()

    def count_by_currency(self):
        """Get count of payments grouped by currency."""
        return self.get_queryset().count_by_currency()

    # User-based methods
    def by_user(self, user):
        """Get payments by user."""
        return self.get_queryset().by_user(user)

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
            'total_amount_usd': float(queryset.total_amount()),
            'average_amount_usd': float(queryset.average_amount()),
            'completed_payments': queryset.completed().count(),
            'pending_payments': queryset.pending().count(),
            'failed_payments': queryset.failed().count(),
            'partially_paid_payments': queryset.partially_paid().count(),
            'by_status': list(queryset.count_by_status()),
            'by_currency': list(queryset.count_by_currency()),
        }

        logger.info(f"Generated payment stats for {days} days", extra={
            'days': days,
            'total_payments': stats['total_payments'],
            'total_amount': stats['total_amount_usd']
        })

        return stats

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
            'total_amount_usd': float(user_payments.total_amount()),
            'completed_payments': user_payments.completed().count(),
            'pending_payments': user_payments.pending().count(),
            'failed_payments': user_payments.failed().count(),
            'last_payment_at': user_payments.first().created_at if user_payments.exists() else None,
            'average_amount_usd': float(user_payments.average_amount()),
        }

        return summary

    # Business logic methods
    def update_payment_status(
        self,
        payment,
        new_status: str,
        extra_fields: Optional[PaymentStatusUpdateFields] = None
    ) -> bool:
        """
        Update payment status with automatic status_changed_at tracking.

        Args:
            payment: Payment instance
            new_status: New status value
            extra_fields: Typed extra fields to update (Pydantic model)

        Returns:
            bool: True if status was updated
        """
        try:
            old_status = payment.status

            # Only update if status actually changed
            if old_status != new_status:
                payment.status = new_status
                payment.status_changed_at = timezone.now()

                # Update fields list for save()
                update_fields = ['status', 'status_changed_at', 'updated_at']

                # Set completed_at if status changed to completed
                if new_status == 'completed' and not payment.completed_at:
                    payment.completed_at = timezone.now()
                    update_fields.append('completed_at')

                # Apply extra fields if provided
                if extra_fields:
                    # Validate extra fields (Pydantic v2)
                    if isinstance(extra_fields, dict):
                        extra_fields = PaymentStatusUpdateFields(**extra_fields)

                    # Apply non-None fields
                    for field_name, field_value in extra_fields.model_dump(exclude_none=True).items():
                        if hasattr(payment, field_name):
                            setattr(payment, field_name, field_value)
                            if field_name not in update_fields:
                                update_fields.append(field_name)
                        else:
                            logger.warning(f"Unknown field {field_name} ignored", extra={
                                'payment_id': str(payment.id),
                                'field_name': field_name
                            })

                payment.save(update_fields=update_fields)

                logger.info("Payment status updated", extra={
                    'payment_id': str(payment.id),
                    'old_status': old_status,
                    'new_status': new_status,
                    'updated_fields': update_fields
                })

                return True
            else:
                logger.debug("Payment status unchanged", extra={
                    'payment_id': str(payment.id),
                    'status': new_status
                })
                return False

        except Exception as e:
            logger.error(f"Failed to update payment status: {e}", extra={
                'payment_id': str(payment.id),
                'old_status': old_status if 'old_status' in locals() else 'unknown',
                'new_status': new_status
            })
            return False
