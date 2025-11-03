"""
Currency model for Payments v2.0.

Simplified currency model focused on NowPayments integration.
NowPayments combines token+network in one code (e.g., USDTTRC20, USDTERC20).
"""

from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models

from .base import TimestampedModel


class Currency(TimestampedModel):
    """
    Universal currency model supporting crypto tokens on different networks.

    For NowPayments:
    - code = "USDTTRC20" (token+network combined)
    - name = "USDT (TRC20)"
    - token = "USDT"
    - network = "TRC20"
    """

    code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        validators=[MinLengthValidator(3), MaxLengthValidator(20)],
        help_text="Currency code from provider (e.g., USDTTRC20, BTC, ETH)"
    )

    name = models.CharField(
        max_length=100,
        help_text="Full currency name (e.g., USDT (TRC20), Bitcoin)"
    )

    # Token and network parsed from NowPayments code
    token = models.CharField(
        max_length=20,
        help_text="Token symbol (e.g., USDT, BTC, ETH)"
    )

    network = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Network name (e.g., TRC20, ERC20, Bitcoin)"
    )

    symbol = models.CharField(
        max_length=10,
        blank=True,
        help_text="Currency symbol (e.g., ₮, ₿, Ξ)"
    )

    decimal_places = models.PositiveSmallIntegerField(
        default=8,
        help_text="Number of decimal places for this currency"
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this currency is available for payments"
    )

    # Provider information (always nowpayments for v2.0)
    provider = models.CharField(
        max_length=50,
        default='nowpayments',
        help_text="Payment provider (always nowpayments for v2.0)"
    )

    # Minimum amount from provider
    min_amount_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1.0,
        help_text="Minimum payment amount in USD"
    )

    # Sort order for display
    sort_order = models.PositiveIntegerField(
        default=0,
        help_text="Sort order for currency list (lower = higher priority)"
    )

    class Meta:
        db_table = 'payments_currencies'
        verbose_name = 'Currency'
        verbose_name_plural = 'Currencies'
        ordering = ['sort_order', 'token', 'network']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['code']),
            models.Index(fields=['token']),
            models.Index(fields=['sort_order']),
        ]

    def __str__(self):
        return f"{self.token} ({self.network})" if self.network else self.token

    def clean(self):
        """Validate currency data."""
        if self.code:
            self.code = self.code.upper()

        if self.token:
            self.token = self.token.upper()

    @property
    def display_name(self) -> str:
        """Human-readable display name."""
        if self.network and self.network.lower() not in ['bitcoin', 'ethereum', 'litecoin']:
            return f"{self.token} ({self.network})"
        return self.token

    @property
    def full_name(self) -> str:
        """Full name with network."""
        return self.name
