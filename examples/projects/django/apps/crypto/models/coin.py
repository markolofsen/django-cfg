"""
Coin model - Cryptocurrency information.
"""

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Coin(models.Model):
    """Cryptocurrency model."""

    # Basic info
    symbol = models.CharField(max_length=10, unique=True, help_text="Coin symbol (e.g., BTC, ETH)")
    name = models.CharField(max_length=100, help_text="Full name (e.g., Bitcoin, Ethereum)")
    slug = models.SlugField(max_length=100, unique=True)

    # Market data
    current_price_usd = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Current price in USD"
    )
    market_cap_usd = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=Decimal('0'),
        help_text="Market capitalization"
    )
    volume_24h_usd = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=Decimal('0'),
        help_text="24h trading volume"
    )

    # Price changes
    price_change_24h_percent = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    price_change_7d_percent = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    price_change_30d_percent = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))

    # Metadata
    logo_url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    whitepaper_url = models.URLField(blank=True)

    # Rankings
    rank = models.PositiveIntegerField(default=0, help_text="Market cap rank")

    # Flags
    is_active = models.BooleanField(default=True)
    is_tradeable = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Coin'
        verbose_name_plural = 'Coins'
        ordering = ['rank', 'symbol']
        indexes = [
            models.Index(fields=['symbol']),
            models.Index(fields=['rank']),
            models.Index(fields=['is_active', 'is_tradeable']),
        ]

    def __str__(self):
        return f"{self.symbol} - {self.name}"

    @property
    def is_price_up_24h(self):
        return self.price_change_24h_percent > 0
