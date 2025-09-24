"""
Balance and transaction models for the universal payments system.
"""

from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from .base import UUIDTimestampedModel, TimestampedModel

User = get_user_model()


class UserBalance(TimestampedModel):
    """User balance model for tracking USD funds."""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='balance',
        help_text="User who owns this balance"
    )
    amount_usd = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        help_text="Current balance in USD"
    )
    reserved_usd = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        help_text="Reserved balance in USD (for pending transactions)"
    )
    total_earned = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        help_text="Total amount earned (lifetime)"
    )
    total_spent = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        help_text="Total amount spent (lifetime)"
    )
    last_transaction_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the last transaction occurred"
    )

    # Import and assign manager
    from ..managers import UserBalanceManager
    objects = UserBalanceManager()

    class Meta:
        db_table = 'user_balances'
        verbose_name = "User Balance"
        verbose_name_plural = "User Balances"
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['amount_usd']),
            models.Index(fields=['last_transaction_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - ${self.amount_usd}"

    @property
    def total_balance(self) -> float:
        """Get total balance (available + reserved)."""
        return self.amount_usd + self.reserved_usd

    @property
    def has_sufficient_funds(self) -> bool:
        """Check if user has sufficient available funds."""
        return self.amount_usd > 0

    def can_debit(self, amount: float) -> bool:
        """Check if user can be debited the specified amount."""
        return self.amount_usd >= amount

    def get_transaction_summary(self):
        """Get transaction summary for this user."""
        transactions = self.user.transactions.all()
        return {
            'total_transactions': transactions.count(),
            'total_payments': transactions.filter(transaction_type=Transaction.TransactionType.PAYMENT).count(),
            'total_subscriptions': transactions.filter(transaction_type=Transaction.TransactionType.SUBSCRIPTION).count(),
            'total_refunds': transactions.filter(transaction_type=Transaction.TransactionType.REFUND).count(),
        }


class Transaction(UUIDTimestampedModel):
    """Transaction history model."""
    
    class TransactionType(models.TextChoices):
        PAYMENT = "payment", "Payment"
        SUBSCRIPTION = "subscription", "Subscription"
        REFUND = "refund", "Refund"
        CREDIT = "credit", "Credit"
        DEBIT = "debit", "Debit"
        HOLD = "hold", "Hold"
        RELEASE = "release", "Release"
        FEE = "fee", "Fee"
        ADJUSTMENT = "adjustment", "Adjustment"
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='transactions',
        help_text="User who made this transaction"
    )
    amount_usd = models.FloatField(
        help_text="Transaction amount in USD (positive for credits, negative for debits)"
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
        help_text="Type of transaction"
    )
    description = models.TextField(
        help_text="Human-readable description of the transaction"
    )
    balance_before = models.FloatField(
        help_text="User balance before this transaction"
    )
    balance_after = models.FloatField(
        help_text="User balance after this transaction"
    )
    
    # Related objects (nullable for flexibility)
    from .payments import UniversalPayment
    from .subscriptions import Subscription
    payment = models.ForeignKey(
        UniversalPayment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions',
        help_text="Related payment (if applicable)"
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions',
        help_text="Related subscription (if applicable)"
    )
    
    # Additional metadata
    reference_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="External reference ID"
    )
    metadata = models.JSONField(
        default=dict,
        help_text="Additional transaction metadata"
    )

    class Meta:
        db_table = 'user_transactions'
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['amount_usd']),
            models.Index(fields=['created_at']),
            models.Index(fields=['reference_id']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        sign = "+" if self.amount_usd >= 0 else ""
        return f"{self.user.email} - {sign}${self.amount_usd} ({self.get_transaction_type_display()})"

    @property
    def is_credit(self) -> bool:
        """Check if this is a credit transaction."""
        return self.amount_usd > 0

    @property
    def is_debit(self) -> bool:
        """Check if this is a debit transaction."""
        return self.amount_usd < 0

    def clean(self):
        """Validate transaction data."""
        
        # Validate balance calculation
        expected_balance = self.balance_before + self.amount_usd
        if abs(expected_balance - self.balance_after) > 0.01:  # Allow for rounding
            raise ValidationError(
                f"Balance calculation error: {self.balance_before} + {self.amount_usd} != {self.balance_after}"
            )
        
        # Validate transaction type and amount sign
        if self.transaction_type == self.TransactionType.PAYMENT and self.amount_usd <= 0:
            raise ValidationError("Payment transactions must have positive amounts")
        
        if self.transaction_type == self.TransactionType.SUBSCRIPTION and self.amount_usd >= 0:
            raise ValidationError("Subscription transactions must have negative amounts")

    def save(self, *args, **kwargs):
        """Override save to run validation."""
        self.clean()
        super().save(*args, **kwargs)
