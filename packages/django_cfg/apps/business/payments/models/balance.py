"""
Balance and transaction models for Payments v2.0.

ORM-based balance calculation from transactions.
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from .base import UUIDTimestampedModel

User = get_user_model()


class UserBalance(models.Model):
    """
    User balance model.

    Balance is calculated from Transaction records via ORM aggregation.
    This model stores the computed balance for performance.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='payment_balance_v2',
        help_text="User who owns this balance"
    )

    balance_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Current balance in USD"
    )

    # Tracking fields
    total_deposited = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Total amount deposited (lifetime)"
    )

    total_withdrawn = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Total amount withdrawn (lifetime)"
    )

    last_transaction_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the last transaction occurred"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Manager
    from .managers.balance_managers import UserBalanceManager
    objects = UserBalanceManager()

    class Meta:
        db_table = 'payments_user_balances'
        verbose_name = 'User Balance'
        verbose_name_plural = 'User Balances'
        indexes = [
            models.Index(fields=['balance_usd']),
            models.Index(fields=['last_transaction_at']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(balance_usd__gte=0.0),
                name='payments_balance_non_negative_check'
            ),
        ]

    def __str__(self):
        return f"{self.user.username}: ${self.balance_usd:.2f}"

    def clean(self):
        """Validate balance data."""
        if self.balance_usd < 0:
            raise ValidationError("Balance cannot be negative")

    @property
    def balance_display(self) -> str:
        """Formatted balance display."""
        return f"${self.balance_usd:.2f} USD"

    @property
    def is_empty(self) -> bool:
        """Check if balance is zero."""
        return self.balance_usd == Decimal('0.00')

    @property
    def has_transactions(self) -> bool:
        """Check if user has any transactions."""
        return self.last_transaction_at is not None

    @classmethod
    def get_or_create_for_user(cls, user: User) -> 'UserBalance':
        """Get or create balance for user."""
        balance, created = cls.objects.get_or_create(user=user)
        return balance


class Transaction(UUIDTimestampedModel):
    """
    Transaction record for balance changes.

    Immutable record of all balance changes with full audit trail.
    """

    class TransactionType(models.TextChoices):
        DEPOSIT = "deposit", "Deposit"
        WITHDRAWAL = "withdrawal", "Withdrawal"
        PAYMENT = "payment", "Payment"
        REFUND = "refund", "Refund"
        FEE = "fee", "Fee"
        BONUS = "bonus", "Bonus"
        ADJUSTMENT = "adjustment", "Adjustment"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payment_transactions_v2',
        help_text="User who owns this transaction"
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
        db_index=True,
        help_text="Type of transaction"
    )

    # Amount in USD (Decimal for precision, positive for credits, negative for debits)
    amount_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Transaction amount in USD (positive=credit, negative=debit)"
    )

    balance_after = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="User balance after this transaction"
    )

    # Reference to related payment
    payment_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
        help_text="Related payment ID (if applicable)"
    )

    # Transaction details
    description = models.TextField(
        help_text="Transaction description"
    )

    # Metadata for additional information
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional transaction metadata"
    )

    # Reference to withdrawal request
    withdrawal_request_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
        help_text="Related withdrawal request ID (if applicable)"
    )

    # Manager
    from .managers.balance_managers import TransactionManager
    objects = TransactionManager()

    class Meta:
        db_table = 'payments_transactions'
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['transaction_type', 'created_at']),
            models.Index(fields=['payment_id']),
            models.Index(fields=['withdrawal_request_id']),
            models.Index(fields=['amount_usd']),
        ]

    def __str__(self):
        sign = "+" if self.amount_usd >= 0 else ""
        return f"{self.user.username}: {sign}${self.amount_usd:.2f} ({self.transaction_type})"

    def clean(self):
        """Validate transaction data."""
        if self.balance_after < 0:
            raise ValidationError("Balance after transaction cannot be negative")

    @property
    def is_credit(self) -> bool:
        """Check if this is a credit transaction."""
        return self.amount_usd > 0

    @property
    def is_debit(self) -> bool:
        """Check if this is a debit transaction."""
        return self.amount_usd < 0

    @property
    def amount_display(self) -> str:
        """Formatted amount display."""
        sign = "+" if self.amount_usd >= 0 else ""
        return f"{sign}${abs(self.amount_usd):.2f}"

    @property
    def type_color(self) -> str:
        """Get color for transaction type display."""
        colors = {
            self.TransactionType.DEPOSIT: 'success',
            self.TransactionType.PAYMENT: 'primary',
            self.TransactionType.WITHDRAWAL: 'warning',
            self.TransactionType.REFUND: 'info',
            self.TransactionType.FEE: 'secondary',
            self.TransactionType.BONUS: 'success',
            self.TransactionType.ADJUSTMENT: 'secondary',
        }
        return colors.get(self.transaction_type, 'secondary')

    def save(self, *args, **kwargs):
        """Override save to ensure immutability."""
        # Only prevent updates, not creation
        if self.pk and not kwargs.get('force_insert', False):
            # Check if this is actually an update (record exists in DB)
            if Transaction.objects.filter(pk=self.pk).exists():
                raise ValidationError("Transactions are immutable and cannot be modified")
        super().save(*args, **kwargs)
