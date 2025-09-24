"""
Payment manager for UniversalPayment model.
"""

from django.db import models


class UniversalPaymentManager(models.Manager):
    """Manager for UniversalPayment model."""
    
    def create_payment(self, user, amount_usd: float, currency_code: str, provider: str):
        """Create a new payment."""
        payment = self.create(
            user=user,
            amount_usd=amount_usd,
            currency_code=currency_code.upper(),
            provider=provider,
            status=self.model.PaymentStatus.PENDING
        )
        return payment
    
    def get_pending_payments(self, user=None):
        """Get pending payments for user or all users."""
        queryset = self.filter(status=self.model.PaymentStatus.PENDING)
        if user:
            queryset = queryset.filter(user=user)
        return queryset
    
    def get_completed_payments(self, user=None):
        """Get completed payments for user or all users."""
        queryset = self.filter(status=self.model.PaymentStatus.COMPLETED)
        if user:
            queryset = queryset.filter(user=user)
        return queryset
    
    def get_failed_payments(self, user=None):
        """Get failed/expired payments for user or all users."""
        queryset = self.filter(status__in=[
            self.model.PaymentStatus.FAILED, 
            self.model.PaymentStatus.EXPIRED
        ])
        if user:
            queryset = queryset.filter(user=user)
        return queryset
