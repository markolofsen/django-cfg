"""
Wallet model - User's cryptocurrency wallet.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal
from .coin import Coin

User = get_user_model()


class Wallet(models.Model):
    """User's crypto wallet for a specific coin."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crypto_wallets')
    coin = models.ForeignKey(Coin, on_delete=models.CASCADE, related_name='wallets')

    # Balances
    balance = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Available balance"
    )
    locked_balance = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Locked balance (in orders)"
    )

    # Wallet address (optional)
    address = models.CharField(max_length=200, blank=True, help_text="Deposit address")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Wallet'
        verbose_name_plural = 'Wallets'
        unique_together = ('user', 'coin')
        ordering = ['-balance']

    def __str__(self):
        return f"{self.user.username} - {self.coin.symbol} ({self.balance})"

    @property
    def total_balance(self):
        """Total balance (available + locked)."""
        return self.balance + self.locked_balance

    @property
    def value_usd(self):
        """Wallet value in USD."""
        return self.total_balance * self.coin.current_price_usd
