"""
Withdrawal model for Payments v2.0.

Manual withdrawal system with admin approval.
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .base import UUIDTimestampedModel
from .currency import Currency

User = get_user_model()


class WithdrawalRequest(UUIDTimestampedModel):
    """
    Withdrawal request model.

    User requests withdrawal → Admin approves manually → Funds sent off-platform.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        REJECTED = 'rejected', 'Rejected'
        CANCELLED = 'cancelled', 'Cancelled'

    # User and identification
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='withdrawal_requests_v2',
        help_text="User who requested withdrawal"
    )

    internal_withdrawal_id = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Internal withdrawal identifier (WD_YYYYMMDDHHMMSS_UUID)"
    )

    # Financial information
    amount_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('10.0')), MaxValueValidator(Decimal('100000.0'))],
        help_text="Withdrawal amount in USD (min $10)"
    )

    # Cryptocurrency information
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name='withdrawals',
        help_text="Withdrawal currency"
    )

    wallet_address = models.CharField(
        max_length=255,
        help_text="Destination wallet address"
    )

    # Fee calculation
    network_fee_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Network transaction fee in USD"
    )

    service_fee_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Service fee in USD"
    )

    total_fee_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total fee (network + service) in USD"
    )

    final_amount_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Final amount to receive (amount - total_fee)"
    )

    # Crypto amounts
    crypto_amount = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True,
        help_text="Amount in cryptocurrency (calculated at processing time)"
    )

    # Status and processing
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        help_text="Withdrawal status"
    )

    # Transaction details (filled after processing)
    transaction_hash = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        db_index=True,
        help_text="Blockchain transaction hash (after sending)"
    )

    # Admin actions
    admin_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_withdrawals_v2',
        help_text="Admin who processed this withdrawal"
    )

    admin_notes = models.TextField(
        blank=True,
        help_text="Admin notes (reason for rejection, etc.)"
    )

    # Timestamps
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When approved by admin"
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When withdrawal was completed"
    )

    rejected_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When rejected by admin"
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When cancelled by user"
    )

    status_changed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="When status was last changed"
    )

    # Metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata (validation info, etc.)"
    )

    class Meta:
        db_table = 'payments_withdrawal_requests'
        verbose_name = 'Withdrawal Request'
        verbose_name_plural = 'Withdrawal Requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['transaction_hash']),
            models.Index(fields=['status_changed_at']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount_usd__gte=10.0),
                name='payments_withdrawal_min_amount_check'
            ),
            models.CheckConstraint(
                condition=models.Q(final_amount_usd__gte=0.0),
                name='payments_withdrawal_final_amount_check'
            ),
        ]

    def __str__(self):
        return f"{self.internal_withdrawal_id} - ${self.amount_usd} {self.currency.code}"

    def save(self, *args, **kwargs):
        """Override save to generate internal withdrawal ID."""
        if not self.internal_withdrawal_id:
            from django.utils import timezone
            # Generate internal withdrawal ID: WD_YYYYMMDDHHMMSS_UUID8
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            self.internal_withdrawal_id = f"WD_{timestamp}_{str(self.id)[:8]}"

        # Calculate final amount if not set
        if not self.final_amount_usd:
            self.final_amount_usd = self.amount_usd - self.total_fee_usd

        super().save(*args, **kwargs)

    def clean(self):
        """Model validation."""
        # Validate amount limits
        if self.amount_usd and self.amount_usd < Decimal('10.0'):
            raise ValidationError("Minimum withdrawal amount is $10.00")

        # Validate final amount is positive
        if self.final_amount_usd and self.final_amount_usd <= 0:
            raise ValidationError("Final amount must be positive after fees")

        # Validate wallet address
        if self.wallet_address and len(self.wallet_address) < 26:
            raise ValidationError("Invalid wallet address (too short)")

    # Status properties
    @property
    def is_pending(self) -> bool:
        """Check if withdrawal is pending."""
        return self.status == self.Status.PENDING

    @property
    def is_approved(self) -> bool:
        """Check if withdrawal is approved."""
        return self.status == self.Status.APPROVED

    @property
    def is_completed(self) -> bool:
        """Check if withdrawal is completed."""
        return self.status == self.Status.COMPLETED

    @property
    def is_rejected(self) -> bool:
        """Check if withdrawal is rejected."""
        return self.status == self.Status.REJECTED

    @property
    def is_cancelled(self) -> bool:
        """Check if withdrawal is cancelled."""
        return self.status == self.Status.CANCELLED

    @property
    def can_be_cancelled(self) -> bool:
        """Check if withdrawal can be cancelled by user."""
        return self.status in [self.Status.PENDING, self.Status.APPROVED]

    @property
    def can_be_approved(self) -> bool:
        """Check if withdrawal can be approved by admin."""
        return self.status == self.Status.PENDING

    @property
    def can_be_rejected(self) -> bool:
        """Check if withdrawal can be rejected by admin."""
        return self.status in [self.Status.PENDING, self.Status.APPROVED]

    # Display properties
    @property
    def status_color(self) -> str:
        """Get color for status display (Bootstrap classes)."""
        colors = {
            self.Status.PENDING: 'warning',
            self.Status.APPROVED: 'info',
            self.Status.PROCESSING: 'primary',
            self.Status.COMPLETED: 'success',
            self.Status.REJECTED: 'danger',
            self.Status.CANCELLED: 'secondary',
        }
        return colors.get(self.status, 'secondary')

    @property
    def amount_display(self) -> str:
        """Formatted amount display."""
        return f"${self.amount_usd:.2f} USD"

    @property
    def final_amount_display(self) -> str:
        """Formatted final amount display."""
        return f"${self.final_amount_usd:.2f} USD"

    @property
    def total_fee_display(self) -> str:
        """Formatted total fee display."""
        return f"${self.total_fee_usd:.2f} USD"

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
