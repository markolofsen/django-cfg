"""
Enhanced Payment manager for UniversalPayment model with query optimizations.
"""

from django.db import models
from django.utils import timezone
from datetime import timedelta
from django_cfg.modules.django_logger import get_logger

logger = get_logger("payment_manager")


class PaymentQuerySet(models.QuerySet):
    """Custom QuerySet for UniversalPayment with optimizations."""
    
    def with_user(self):
        """Select related user to prevent N+1 queries."""
        return self.select_related('user')
    
    def with_events(self):
        """Skip prefetch for events since they use CharField payment_id, not ForeignKey."""
        # PaymentEvent uses CharField payment_id, not ForeignKey, so no reverse relation exists
        # Events should be fetched separately when needed
        return self
    
    def optimized(self):
        """Get optimized queryset for admin and API views."""
        return self.select_related('user').with_events()
    
    def active(self):
        """Get active payments (not failed, cancelled, or refunded)."""
        return self.exclude(
            status__in=['failed', 'cancelled', 'refunded', 'expired']
        )
    
    def completed(self):
        """Get only completed payments."""
        return self.filter(status='completed')
    
    def pending(self):
        """Get pending payments."""
        return self.filter(status='pending')
    
    def by_provider(self, provider):
        """Filter by payment provider."""
        return self.filter(provider=provider)
    
    def recent(self, days=30):
        """Get payments from last N days."""
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff_date)
    
    def by_amount_range(self, min_amount=None, max_amount=None):
        """Filter by USD amount range."""
        queryset = self
        if min_amount is not None:
            queryset = queryset.filter(amount_usd__gte=min_amount)
        if max_amount is not None:
            queryset = queryset.filter(amount_usd__lte=max_amount)
        return queryset
    
    def by_user(self, user):
        """Filter by user."""
        return self.filter(user=user)
    
    def expired(self):
        """Get expired payments."""
        return self.filter(
            expires_at__lt=timezone.now(),
            status__in=['pending', 'confirming']
        )


class UniversalPaymentManager(models.Manager):
    """Enhanced manager for UniversalPayment with optimization methods."""
    
    def get_queryset(self):
        """Return custom QuerySet."""
        return PaymentQuerySet(self.model, using=self._db)
    
    def with_user(self):
        """Get payments with user data preloaded."""
        return self.get_queryset().with_user()
    
    def optimized(self):
        """Get optimized queryset for admin views."""
        return self.get_queryset().optimized()
    
    def active(self):
        """Get active payments."""
        return self.get_queryset().active()
    
    def completed(self):
        """Get completed payments."""
        return self.get_queryset().completed()
    
    def pending(self):
        """Get pending payments."""
        return self.get_queryset().pending()
    
    def recent(self, days=30):
        """Get recent payments."""
        return self.get_queryset().recent(days)
    
    def by_provider(self, provider):
        """Get payments by provider."""
        return self.get_queryset().by_provider(provider)
    
    def create_payment(self, user, amount_usd: float, currency_code: str, provider: str, **kwargs):
        """Create a payment with automatic field generation."""
        from uuid import uuid4
        
        # Generate unique internal payment ID if not provided
        internal_payment_id = kwargs.pop('internal_payment_id', f"PAY_{uuid4().hex[:8].upper()}")
        
        payment = self.create(
            user=user,
            internal_payment_id=internal_payment_id,
            amount_usd=amount_usd,
            currency_code=currency_code.upper(),
            provider=provider,
            status=self.model.PaymentStatus.PENDING,
            **kwargs
        )
        
        return payment
    
    def get_pending_payments(self, user=None):
        """Get pending payments for user or all users."""
        queryset = self.pending()
        if user:
            queryset = queryset.by_user(user)
        return queryset.with_user()
    
    def get_completed_payments(self, user=None):
        """Get completed payments for user or all users."""
        queryset = self.completed()
        if user:
            queryset = queryset.by_user(user)
        return queryset.with_user()
    
    def get_failed_payments(self, user=None):
        """Get failed/expired payments for user or all users."""
        queryset = self.filter(status__in=[
            self.model.PaymentStatus.FAILED, 
            self.model.PaymentStatus.EXPIRED
        ])
        if user:
            queryset = queryset.by_user(user)
        return queryset.with_user()
    
    def get_user_stats(self, user):
        """Get payment statistics for a user."""
        user_payments = self.by_user(user)
        
        return {
            'total_payments': user_payments.count(),
            'completed_payments': user_payments.completed().count(),
            'pending_payments': user_payments.pending().count(),
            'failed_payments': user_payments.filter(status='failed').count(),
            'total_amount_usd': user_payments.completed().aggregate(
                total=models.Sum('amount_usd')
            )['total'] or 0,
            'recent_payments_30d': user_payments.recent(30).count(),
        }
    
    def get_provider_stats(self, provider=None):
        """Get payment statistics by provider."""
        if provider:
            payments = self.by_provider(provider)
        else:
            payments = self.all()
        
        return {
            'total_payments': payments.count(),
            'completed_payments': payments.completed().count(),
            'pending_payments': payments.pending().count(),
            'success_rate': (
                payments.completed().count() / max(payments.count(), 1) * 100
            ),
            'total_volume_usd': payments.completed().aggregate(
                total=models.Sum('amount_usd')
            )['total'] or 0,
        }
    
    def mark_expired_payments(self):
        """Mark expired payments as expired."""
        expired_count = self.expired().update(
            status=self.model.PaymentStatus.EXPIRED,
            updated_at=timezone.now()
        )
        return expired_count
