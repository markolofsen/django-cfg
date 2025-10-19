"""
Exchange model - Cryptocurrency exchange information.
"""

from django.db import models
from decimal import Decimal


class Exchange(models.Model):
    """Cryptocurrency exchange model."""

    # Basic info
    name = models.CharField(max_length=100, unique=True, help_text="Exchange name")
    slug = models.SlugField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True, help_text="Exchange code (e.g., BINANCE, COINBASE)")

    # Details
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    logo_url = models.URLField(blank=True)

    # Trading data
    volume_24h_usd = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=Decimal('0'),
        help_text="24h trading volume"
    )
    num_markets = models.PositiveIntegerField(default=0, help_text="Number of trading pairs")
    num_coins = models.PositiveIntegerField(default=0, help_text="Number of supported coins")

    # Fees
    maker_fee_percent = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.1'))
    taker_fee_percent = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.1'))

    # Flags
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    supports_api = models.BooleanField(default=True)

    # Rankings
    rank = models.PositiveIntegerField(default=0, help_text="Exchange rank by volume")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Exchange'
        verbose_name_plural = 'Exchanges'
        ordering = ['rank', 'name']

    def __str__(self):
        return self.name
