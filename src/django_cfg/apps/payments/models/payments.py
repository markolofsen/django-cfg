"""
Payment models for the Universal Payment System v2.0.

Core payment model with simplified architecture focused on NowPayments.
"""

from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from .base import UUIDTimestampedModel
from .currencies import Currency, Network

User = get_user_model()


class UniversalPayment(UUIDTimestampedModel):
    """
    Universal payment model supporting all providers.
    
    Simplified v2.0 architecture focused on NowPayments with extensible design.
    Uses float for USD amounts as per requirements for performance and API compatibility.
    """
    
    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMING = "confirming", "Confirming"
        CONFIRMED = "confirmed", "Confirmed"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"
        REFUNDED = "refunded", "Refunded"
    
    class PaymentProvider(models.TextChoices):
        NOWPAYMENTS = "nowpayments", "NowPayments"
        # Future providers can be added here
        
        @classmethod
        def get_crypto_providers(cls):
            """Get list of crypto provider values."""
            return [cls.NOWPAYMENTS]
        
        @classmethod
        def is_crypto_provider(cls, provider_name: str) -> bool:
            """Check if provider handles cryptocurrency."""
            return provider_name in cls.get_crypto_providers()
    
    # User and identification
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payments',
        help_text="User who created this payment"
    )
    
    internal_payment_id = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Internal payment identifier"
    )
    
    # Financial information (USD as float per requirements)
    amount_usd = models.FloatField(
        validators=[MinValueValidator(1.0), MaxValueValidator(50000.0)],
        help_text="Payment amount in USD (float for performance)"
    )
    
    # Cryptocurrency information
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name='payments',
        help_text="Payment currency"
    )
    
    network = models.ForeignKey(
        Network,
        on_delete=models.PROTECT,
        related_name='payments',
        null=True,
        blank=True,
        help_text="Blockchain network (for crypto payments)"
    )
    
    # Crypto amounts use Decimal for precision
    pay_amount = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True,
        help_text="Amount to pay in cryptocurrency (Decimal for precision)"
    )
    
    actual_amount_usd = models.FloatField(
        null=True,
        blank=True,
        help_text="Actual amount received in USD"
    )
    
    fee_amount_usd = models.FloatField(
        null=True,
        blank=True,
        help_text="Fee amount in USD"
    )
    
    # Provider information
    provider = models.CharField(
        max_length=50,
        choices=PaymentProvider.choices,
        default=PaymentProvider.NOWPAYMENTS,
        help_text="Payment provider"
    )
    
    provider_payment_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        help_text="Provider's payment ID"
    )
    
    # Payment details
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True,
        help_text="Current payment status"
    )
    
    pay_address = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Cryptocurrency payment address"
    )
    
    payment_url = models.URLField(
        null=True,
        blank=True,
        help_text="Payment page URL"
    )
    
    # Transaction information
    transaction_hash = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        db_index=True,
        help_text="Blockchain transaction hash"
    )
    
    confirmations_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of blockchain confirmations"
    )
    
    # Security and validation
    security_nonce = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        db_index=True,
        help_text="Security nonce for validation"
    )
    
    # Timestamps
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this payment expires"
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this payment was completed"
    )
    
    # Metadata and description
    description = models.TextField(
        blank=True,
        help_text="Payment description"
    )
    
    callback_url = models.URLField(
        null=True,
        blank=True,
        help_text="Success callback URL"
    )
    
    cancel_url = models.URLField(
        null=True,
        blank=True,
        help_text="Cancellation URL"
    )
    
    # Structured metadata (validated by Pydantic in services)
    provider_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Provider-specific data (validated by Pydantic)"
    )
    
    webhook_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Webhook data (validated by Pydantic)"
    )
    
    # Manager
    from .managers.payment_managers import PaymentManager
    objects = PaymentManager()
    
    class Meta:
        db_table = 'payments_universal'
        verbose_name = 'Universal Payment'
        verbose_name_plural = 'Universal Payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['provider', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['provider_payment_id']),
            models.Index(fields=['transaction_hash']),
            models.Index(fields=['expires_at']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount_usd__gte=1.0),
                name='payments_min_amount_check'
            ),
            models.CheckConstraint(
                check=models.Q(amount_usd__lte=50000.0),
                name='payments_max_amount_check'
            ),
        ]
    
    def __str__(self):
        return f"Payment {self.internal_payment_id} - ${self.amount_usd:.2f} {self.currency.code}"
    
    def save(self, *args, **kwargs):
        """Override save to generate internal payment ID."""
        if not self.internal_payment_id:
            # Generate internal payment ID
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            self.internal_payment_id = f"PAY_{timestamp}_{str(self.id)[:8]}"
        
        super().save(*args, **kwargs)
    
    def clean(self):
        """Model validation."""
        # Crypto payments must have network
        if self.currency and self.currency.is_crypto and not self.network:
            raise ValidationError("Cryptocurrency payments must specify a network")
        
        # Fiat payments should not have network
        if self.currency and self.currency.is_fiat and self.network:
            raise ValidationError("Fiat payments should not specify a network")
        
        # Validate amount limits
        if self.amount_usd and (self.amount_usd < 1.0 or self.amount_usd > 50000.0):
            raise ValidationError("Payment amount must be between $1.00 and $50,000.00")
        
        # Validate expiration
        if self.expires_at and self.expires_at <= timezone.now():
            raise ValidationError("Expiration time must be in the future")
    
    # Status properties
    @property
    def is_pending(self) -> bool:
        """Check if payment is pending."""
        return self.status == self.PaymentStatus.PENDING
    
    @property
    def is_completed(self) -> bool:
        """Check if payment is completed."""
        return self.status == self.PaymentStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if payment failed."""
        return self.status in [
            self.PaymentStatus.FAILED,
            self.PaymentStatus.EXPIRED,
            self.PaymentStatus.CANCELLED
        ]
    
    @property
    def is_expired(self) -> bool:
        """Check if payment is expired."""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at
    
    @property
    def requires_confirmation(self) -> bool:
        """Check if payment requires blockchain confirmation."""
        return self.status in [
            self.PaymentStatus.CONFIRMING,
            self.PaymentStatus.CONFIRMED
        ]
    
    # Display properties
    @property
    def status_color(self) -> str:
        """Get color for status display."""
        colors = {
            self.PaymentStatus.PENDING: 'warning',
            self.PaymentStatus.CONFIRMING: 'info',
            self.PaymentStatus.CONFIRMED: 'primary',
            self.PaymentStatus.COMPLETED: 'success',
            self.PaymentStatus.FAILED: 'danger',
            self.PaymentStatus.EXPIRED: 'secondary',
            self.PaymentStatus.CANCELLED: 'secondary',
            self.PaymentStatus.REFUNDED: 'warning',
        }
        return colors.get(self.status, 'secondary')
    
    @property
    def amount_display(self) -> str:
        """Formatted amount display."""
        return f"${self.amount_usd:.2f} USD"
    
    @property
    def crypto_amount_display(self) -> str:
        """Formatted crypto amount display."""
        if not self.pay_amount:
            return "N/A"
        return f"{self.pay_amount:.8f} {self.currency.code}"
    
    # Business logic methods
    def can_be_cancelled(self) -> bool:
        """Check if payment can be cancelled."""
        return self.status in [
            self.PaymentStatus.PENDING,
            self.PaymentStatus.CONFIRMING
        ]
    
    def can_be_refunded(self) -> bool:
        """Check if payment can be refunded."""
        return self.status == self.PaymentStatus.COMPLETED
    
    def mark_completed(self, actual_amount_usd: float = None, transaction_hash: str = None):
        """Mark payment as completed (delegates to manager)."""
        return self.__class__.objects.mark_payment_completed(
            self, actual_amount_usd, transaction_hash
        )
    
    def mark_failed(self, reason: str = None, error_code: str = None):
        """Mark payment as failed (delegates to manager)."""
        return self.__class__.objects.mark_payment_failed(
            self, reason, error_code
        )
    
    def cancel(self, reason: str = None):
        """Cancel payment (delegates to manager)."""
        return self.__class__.objects.cancel_payment(self, reason)
