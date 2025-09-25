"""
Currency models for the universal payments system - KISS version.
"""

from django.db import models
from .base import TimestampedModel

# Currency converter import moved inside methods to avoid circular imports

class Currency(TimestampedModel):
    """Base currencies - clean, no provider-specific codes."""
    
    class CurrencyType(models.TextChoices):
        FIAT = "fiat", "Fiat Currency"
        CRYPTO = "crypto", "Cryptocurrency"
    
    # Core fields - only essentials
    code = models.CharField(
        max_length=10,
        unique=True,
        help_text="Clean currency code: BTC, USDT, ETH, USD (NO network suffixes)"
    )
    name = models.CharField(
        max_length=100,
        help_text="Currency name: Bitcoin, Tether USD, Ethereum"
    )
    currency_type = models.CharField(
        max_length=10,
        choices=CurrencyType.choices,
        help_text="fiat or crypto"
    )
    
    # USD rate caching - updated once per day
    usd_rate = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True,
        help_text="Cached USD exchange rate (1 CURRENCY = X USD)"
    )
    
    rate_updated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the USD rate was last updated"
    )
    
    # Import manager
    from ..managers.currency_manager import CurrencyManager
    objects = CurrencyManager()
    
    class Meta:
        db_table = 'payment_currencies'
        verbose_name = "Currency"
        verbose_name_plural = "Currencies"
        ordering = ['currency_type', 'code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def is_fiat(self) -> bool:
        return self.currency_type == self.CurrencyType.FIAT
    
    @property
    def is_crypto(self) -> bool:
        return self.currency_type == self.CurrencyType.CRYPTO


class Network(TimestampedModel):
    """Blockchain networks - code and name only."""
    
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Network code: ethereum, bitcoin, tron, bsc"
    )
    name = models.CharField(
        max_length=100,
        help_text="Network name: Ethereum, Bitcoin, TRON, BSC"
    )
    
    # Import manager
    from ..managers.currency_manager import NetworkManager
    objects = NetworkManager()
    
    class Meta:
        db_table = 'payment_networks'
        verbose_name = "Network"
        verbose_name_plural = "Networks"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class ProviderCurrency(TimestampedModel):
    """Provider-currency-network mapping - minimal."""
    
    # Identification
    provider_name = models.CharField(
        max_length=50,
        help_text="Provider: nowpayments, stripe, cryptomus"
    )
    provider_currency_code = models.CharField(
        max_length=20,
        help_text="Provider code: USDTERC20, USDTBSC, usd"
    )
    
    # Links to clean models
    base_currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name='provider_mappings',
        help_text="Base currency: BTC, USDT, ETH"
    )
    network = models.ForeignKey(
        Network,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='provider_currencies',
        help_text="Network for crypto (null for fiat)"
    )
    
    # Universal provider fields - common across providers
    min_amount = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True,
        help_text="Minimum payment amount"
    )
    max_amount = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True,
        help_text="Maximum payment amount (null = no limit)"
    )
    
    # Status and availability
    is_enabled = models.BooleanField(
        default=True,
        help_text="Enabled by provider"
    )
    available_for_payment = models.BooleanField(
        default=True,
        help_text="Can receive payments"
    )
    available_for_payout = models.BooleanField(
        default=True,
        help_text="Can send payouts"
    )
    
    # Classification for UI
    is_popular = models.BooleanField(
        default=False,
        help_text="Popular/recommended by provider"
    )
    is_stable = models.BooleanField(
        default=False,
        help_text="Stable coin (USDT, USDC, etc.)"
    )
    priority = models.IntegerField(
        default=0,
        help_text="Display priority (higher = shown first)"
    )
    logo_url = models.URLField(
        blank=True,
        help_text="Currency logo/icon URL from provider"
    )
    
    # Raw provider data - everything else goes here
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="All provider-specific data: logo_url, smart_contract, wallet_regex, commission_percent, etc."
    )
    
    # Import manager
    from ..managers.currency_manager import ProviderCurrencyManager
    objects = ProviderCurrencyManager()
    
    class Meta:
        db_table = 'payment_provider_currencies'
        verbose_name = "Provider Currency"
        verbose_name_plural = "Provider Currencies"
        unique_together = [
            ('provider_name', 'provider_currency_code'),
            ('provider_name', 'base_currency', 'network')
        ]
        ordering = ['-priority', 'provider_name', 'base_currency__code']
    
    def __str__(self):
        network_part = f" ({self.network.code})" if self.network else ""
        return f"{self.provider_name}: {self.base_currency.code}{network_part}"
    
    @property
    def display_name(self) -> str:
        """Human-readable name."""
        if self.network:
            return f"{self.base_currency.name} ({self.network.name})"
        return self.base_currency.name
    
    # Metadata helper properties
    
    def is_amount_valid(self, amount) -> bool:
        """Check if amount is within provider limits."""
        if not amount:
            return False
            
        if self.min_amount and amount < self.min_amount:
            return False
            
        if self.max_amount and amount > self.max_amount:
            return False
            
        return True
    
    def get_validation_errors(self, amount) -> list:
        """Get validation errors for amount."""
        errors = []
        
        if not amount:
            errors.append("Amount is required")
            return errors
            
        if self.min_amount and amount < self.min_amount:
            errors.append(f"Amount must be at least {self.min_amount}")
            
        if self.max_amount and amount > self.max_amount:
            errors.append(f"Amount must not exceed {self.max_amount}")
            
        return errors
    
    @property
    def usd_rate(self) -> float:
        """Get USD rate for base currency (1 CURRENCY = X USD)."""
        return Currency.objects.get_usd_rate(self.base_currency.code)
    
    @property 
    def tokens_per_usd(self) -> float:
        """Get how many tokens you can buy for 1 USD."""
        return Currency.objects.get_tokens_per_usd(self.base_currency.code)
    
    def convert_to_usd(self, amount: float) -> float:
        """Convert amount of this currency to USD."""
        return Currency.objects.convert_to_usd(amount, self.base_currency.code)
    
    def convert_from_usd(self, usd_amount: float) -> float:
        """Convert USD amount to this currency."""
        return Currency.objects.convert_from_usd(usd_amount, self.base_currency.code)

