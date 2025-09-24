"""
Currency models for the universal payments system.
"""

from django.db import models
from .base import TimestampedModel


class Currency(TimestampedModel):
    """Supported currencies for payments."""
    
    class CurrencyType(models.TextChoices):
        FIAT = "fiat", "Fiat Currency"
        CRYPTO = "crypto", "Cryptocurrency"
    
    code = models.CharField(
        max_length=10,
        unique=True,
        help_text="Currency code (e.g., USD, BTC, ETH)"
    )
    name = models.CharField(
        max_length=100,
        help_text="Full currency name"
    )
    symbol = models.CharField(
        max_length=10,
        help_text="Currency symbol (e.g., $, ₿, Ξ)"
    )
    currency_type = models.CharField(
        max_length=10,
        choices=CurrencyType.choices,
        help_text="Type of currency"
    )
    decimal_places = models.PositiveSmallIntegerField(
        default=2,
        help_text="Number of decimal places for this currency"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this currency is active for payments"
    )
    min_payment_amount = models.FloatField(
        default=1.0,
        help_text="Minimum payment amount for this currency"
    )
    
    # Exchange rate to USD (base currency)
    usd_rate = models.FloatField(
        default=1.0,
        help_text="Exchange rate to USD (1 unit of this currency = X USD)"
    )
    rate_updated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the exchange rate was last updated"
    )
    
    # Import and assign manager
    from ..managers import CurrencyManager
    objects = CurrencyManager()
    
    class Meta:
        db_table = 'payment_currencies'
        verbose_name = "Currency"
        verbose_name_plural = "Currencies"
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['currency_type']),
            models.Index(fields=['is_active']),
        ]
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def is_fiat(self) -> bool:
        """Check if this is a fiat currency."""
        return self.currency_type == self.CurrencyType.FIAT
    
    @property
    def is_crypto(self) -> bool:
        """Check if this is a cryptocurrency."""
        return self.currency_type == self.CurrencyType.CRYPTO
    
    def to_usd(self, amount: float) -> float:
        """Convert amount of this currency to USD."""
        return amount * self.usd_rate
    
    def from_usd(self, usd_amount: float) -> float:
        """Convert USD amount to this currency."""
        if self.usd_rate == 0:
            return 0
        return usd_amount / self.usd_rate


class CurrencyNetwork(TimestampedModel):
    """Networks/blockchains for cryptocurrencies."""
    
    currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name='networks',
        help_text="Currency this network supports"
    )
    network_name = models.CharField(
        max_length=50,
        help_text="Network name (e.g., mainnet, polygon, bsc)"
    )
    network_code = models.CharField(
        max_length=20,
        help_text="Network code for API integration"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this network is active"
    )
    confirmation_blocks = models.PositiveIntegerField(
        default=1,
        help_text="Number of confirmations required"
    )
    
    # Import and assign manager
    from ..managers import CurrencyNetworkManager
    objects = CurrencyNetworkManager()
    
    class Meta:
        db_table = 'payment_currency_networks'
        verbose_name = "Currency Network"
        verbose_name_plural = "Currency Networks"
        unique_together = [['currency', 'network_code']]
        indexes = [
            models.Index(fields=['currency', 'is_active']),
            models.Index(fields=['network_code']),
        ]
    
    def __str__(self):
        return f"{self.currency.code} - {self.network_name}"
