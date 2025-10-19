"""
Payment model for Payments v2.0.

Simplified payment model focused on NowPayments with polling-based flow.
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from .base import UUIDTimestampedModel
from .currency import Currency

User = get_user_model()


class Payment(UUIDTimestampedModel):
    """
    Payment model for cryptocurrency deposits via NowPayments.

    Simplified v2.0 architecture:
    - No webhooks (polling instead)
    - Single provider (NowPayments)
    - No callbacks/cancel_url
    - No security_nonce
    """

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMING = "confirming", "Confirming"
        CONFIRMED = "confirmed", "Confirmed"
        COMPLETED = "completed", "Completed"
        PARTIALLY_PAID = "partially_paid", "Partially Paid"
        FAILED = "failed", "Failed"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"

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
        help_text="Internal payment identifier (PAY_YYYYMMDDHHMMSS_UUID)"
    )

    # Financial information (Decimal for precision)
    amount_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('1.0')), MaxValueValidator(Decimal('50000.0'))],
        help_text="Payment amount in USD"
    )

    # Cryptocurrency information
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name='payments',
        help_text="Payment currency (e.g., USDTTRC20)"
    )

    # Crypto amounts use Decimal for precision
    pay_amount = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True,
        help_text="Amount to pay in cryptocurrency"
    )

    actual_amount = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True,
        help_text="Actual amount received in cryptocurrency"
    )

    actual_amount_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual amount received in USD"
    )

    # Provider information (always nowpayments)
    provider = models.CharField(
        max_length=50,
        default='nowpayments',
        help_text="Payment provider (always nowpayments)"
    )

    provider_payment_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        unique=True,
        db_index=True,
        help_text="NowPayments payment ID"
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
        help_text="Payment page URL (if provided by provider)"
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

    # Timestamps
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="When this payment expires (typically 30 minutes)"
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this payment was completed"
    )

    status_changed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="When the payment status was last changed"
    )

    # Metadata
    description = models.TextField(
        blank=True,
        help_text="Payment description"
    )

    # Provider response data (for debugging and audit)
    provider_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Provider-specific data (raw response, etc.)"
    )

    # Manager
    from .managers.payment_managers import PaymentManager
    objects = PaymentManager()

    class Meta:
        db_table = 'payments_payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['provider_payment_id']),
            models.Index(fields=['transaction_hash']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['status_changed_at']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount_usd__gte=1.0),
                name='payments_min_amount_check'
            ),
            models.CheckConstraint(
                condition=models.Q(amount_usd__lte=50000.0),
                name='payments_max_amount_check'
            ),
        ]

    def __str__(self):
        return f"{self.internal_payment_id} - ${self.amount_usd} {self.currency.code}"

    def save(self, *args, **kwargs):
        """Override save to generate internal payment ID."""
        if not self.internal_payment_id:
            # Generate internal payment ID: PAY_YYYYMMDDHHMMSS_UUID8
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            self.internal_payment_id = f"PAY_{timestamp}_{str(self.id)[:8]}"

        super().save(*args, **kwargs)

    def clean(self):
        """Model validation."""
        # Validate amount limits
        if self.amount_usd and (self.amount_usd < Decimal('1.0') or self.amount_usd > Decimal('50000.0')):
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
    def is_partially_paid(self) -> bool:
        """Check if payment is partially paid."""
        return self.status == self.PaymentStatus.PARTIALLY_PAID

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
        """Get color for status display (Bootstrap classes)."""
        colors = {
            self.PaymentStatus.PENDING: 'warning',
            self.PaymentStatus.CONFIRMING: 'info',
            self.PaymentStatus.CONFIRMED: 'primary',
            self.PaymentStatus.COMPLETED: 'success',
            self.PaymentStatus.PARTIALLY_PAID: 'warning',
            self.PaymentStatus.FAILED: 'danger',
            self.PaymentStatus.EXPIRED: 'secondary',
            self.PaymentStatus.CANCELLED: 'secondary',
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
        return f"{self.pay_amount:.8f} {self.currency.token}"

    # QR code and explorer links
    @property
    def qr_data(self) -> str:
        """Generate QR code data for payment."""
        if not self.pay_address:
            return None

        # For most crypto, just use the address
        # Can be enhanced later for specific URI formats (bitcoin:, ethereum:, etc.)
        return self.pay_address

    def get_qr_code_url(self, size=200) -> str:
        """Generate QR code URL using external service."""
        if not self.qr_data:
            return None

        from urllib.parse import quote
        qr_data_encoded = quote(self.qr_data)
        return f"https://api.qrserver.com/v1/create-qr-code/?size={size}x{size}&data={qr_data_encoded}"

    def get_explorer_link(self) -> str:
        """Generate blockchain explorer link for transaction."""
        if not self.transaction_hash:
            return ""

        # Detect network from currency and generate explorer URL
        network = self.currency.network.lower() if self.currency.network else ''

        # Explorer URL templates
        explorer_templates = {
            'bitcoin': 'https://blockstream.info/tx/{txid}',
            'ethereum': 'https://etherscan.io/tx/{txid}',
            'erc20': 'https://etherscan.io/tx/{txid}',
            'tron': 'https://tronscan.org/#/transaction/{txid}',
            'trc20': 'https://tronscan.org/#/transaction/{txid}',
            'polygon': 'https://polygonscan.com/tx/{txid}',
            'bsc': 'https://bscscan.com/tx/{txid}',
            'binance smart chain': 'https://bscscan.com/tx/{txid}',
            'litecoin': 'https://blockchair.com/litecoin/transaction/{txid}',
            'arbitrum': 'https://arbiscan.io/tx/{txid}',
            'optimism': 'https://optimistic.etherscan.io/tx/{txid}',
            'avalanche': 'https://snowtrace.io/tx/{txid}',
        }

        template = explorer_templates.get(network)
        if template:
            return template.format(txid=self.transaction_hash)

        return ""

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
