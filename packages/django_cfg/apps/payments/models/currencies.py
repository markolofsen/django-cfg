"""
Currency models for the Universal Payment System v2.0.

Handles multi-provider currency support with integration to django_currency module.
"""

from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from .base import TimestampedModel


class Currency(TimestampedModel):
    """
    Universal currency model supporting both fiat and crypto.
    
    Integrates with django_currency module for rate conversion.
    """
    
    class CurrencyType(models.TextChoices):
        FIAT = "fiat", "Fiat Currency"
        CRYPTO = "crypto", "Cryptocurrency"
    
    code = models.CharField(
        max_length=10,
        unique=True,
        validators=[MinLengthValidator(3), MaxLengthValidator(10)],
        help_text="Currency code (e.g., BTC, USD, ETH)"
    )
    
    name = models.CharField(
        max_length=100,
        help_text="Full currency name (e.g., Bitcoin, US Dollar)"
    )
    
    currency_type = models.CharField(
        max_length=10,
        choices=CurrencyType.choices,
        help_text="Type of currency"
    )
    
    symbol = models.CharField(
        max_length=10,
        blank=True,
        help_text="Currency symbol (e.g., $, ₿, Ξ)"
    )
    
    decimal_places = models.PositiveSmallIntegerField(
        default=8,
        help_text="Number of decimal places for this currency"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this currency is available for payments"
    )
    
    # Integration with django_currency
    exchange_rate_source = models.CharField(
        max_length=50,
        blank=True,
        help_text="Source for exchange rates (auto-detected by django_currency)"
    )
    
    usd_rate = models.FloatField(
        default=1.0,
        help_text="Current USD exchange rate (1 unit = X USD)"
    )
    
    usd_rate_updated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When USD rate was last updated"
    )
    
    # Manager
    from .managers.currency_managers import CurrencyManager
    objects = CurrencyManager()
    
    class Meta:
        db_table = 'payments_currencies'
        verbose_name = 'Currency'
        verbose_name_plural = 'Currencies'
        ordering = ['currency_type', 'code']
        indexes = [
            models.Index(fields=['currency_type', 'is_active']),
            models.Index(fields=['code']),
        ]
    
    def __str__(self):
        return f"{self.code} ({self.name})"
    
    def clean(self):
        """Validate currency data."""
        if self.code:
            self.code = self.code.upper()
        
        # Validate decimal places based on currency type
        if self.currency_type == self.CurrencyType.FIAT and self.decimal_places > 4:
            raise ValidationError("Fiat currencies should not have more than 4 decimal places")
        
        if self.currency_type == self.CurrencyType.CRYPTO and self.decimal_places > 18:
            raise ValidationError("Crypto currencies should not have more than 18 decimal places")
    
    @property
    def is_crypto(self) -> bool:
        """Check if this is a cryptocurrency."""
        return self.currency_type == self.CurrencyType.CRYPTO
    
    @property
    def is_fiat(self) -> bool:
        """Check if this is a fiat currency."""
        return self.currency_type == self.CurrencyType.FIAT
    
    def get_provider_config(self, provider: str):
        """
        Get provider configuration for this currency.
        
        Args:
            provider: Provider name (e.g., 'nowpayments')
        
        Returns:
            dict: Provider configuration or None
        """
        return Currency.objects.get_provider_config(self.code, provider)
    


class Network(TimestampedModel):
    """
    Blockchain network model for cryptocurrency payments.
    
    Represents different networks like Ethereum, Bitcoin, Polygon, etc.
    """
    
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Network name (e.g., Ethereum, Bitcoin, Polygon)"
    )
    
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Network code (e.g., ETH, BTC, MATIC)"
    )
    
    native_currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name='native_networks',
        help_text="Native currency of this network"
    )
    
    block_explorer_url = models.URLField(
        blank=True,
        help_text="Block explorer URL template (use {tx} for transaction hash)"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this network is available for payments"
    )
    
    # Network-specific settings
    confirmation_blocks = models.PositiveIntegerField(
        default=1,
        help_text="Number of confirmations required for this network"
    )
    
    average_block_time = models.PositiveIntegerField(
        default=600,  # 10 minutes in seconds
        help_text="Average block time in seconds"
    )
    
    class Meta:
        db_table = 'payments_networks'
        verbose_name = 'Network'
        verbose_name_plural = 'Networks'
        ordering = ['name']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['code']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def clean(self):
        """Validate network data."""
        if self.code:
            self.code = self.code.upper()
    
    @property
    def estimated_confirmation_time(self) -> int:
        """Estimated time for confirmations in seconds."""
        return self.confirmation_blocks * self.average_block_time


class ProviderCurrency(TimestampedModel):
    """
    Provider-specific currency configuration.
    
    Maps currencies to specific providers and networks.
    """
    
    provider = models.CharField(
        max_length=50,
        help_text="Payment provider name (e.g., nowpayments)"
    )
    
    currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name='provider_configs'
    )
    
    network = models.ForeignKey(
        Network,
        on_delete=models.CASCADE,
        related_name='provider_configs',
        null=True,
        blank=True,
        help_text="Network for crypto currencies (null for fiat)"
    )
    
    # Provider-specific settings
    provider_currency_code = models.CharField(
        max_length=20,
        help_text="Currency code as used by the provider"
    )
    
# min_amount and max_amount removed - now provided by provider configuration properties
    
    is_enabled = models.BooleanField(
        default=True,
        help_text="Whether this currency is enabled for this provider"
    )
    
    # Fee configuration removed - now provided by provider configuration properties
    
    class Meta:
        db_table = 'payments_provider_currencies'
        verbose_name = 'Provider Currency'
        verbose_name_plural = 'Provider Currencies'
        unique_together = [['provider', 'currency', 'network']]
        ordering = ['provider', 'currency__code']
        indexes = [
            models.Index(fields=['provider', 'is_enabled']),
            models.Index(fields=['currency', 'is_enabled']),
        ]
    
    def __str__(self):
        network_part = f" ({self.network.code})" if self.network else ""
        return f"{self.provider}: {self.currency.code}{network_part}"
    
    def clean(self):
        """Validate provider currency configuration."""
        # Crypto currencies must have a network
        if self.currency and self.currency.is_crypto and not self.network:
            raise ValidationError("Crypto currencies must specify a network")
        
        # Fiat currencies should not have a network
        if self.currency and self.currency.is_fiat and self.network:
            raise ValidationError("Fiat currencies should not specify a network")
        
        # Amount limits validation removed - now handled by provider configuration
    
    @property
    def display_name(self) -> str:
        """Human-readable display name."""
        network_part = f" on {self.network.name}" if self.network else ""
        return f"{self.currency.name}{network_part}"
    
    # Provider configuration properties (get values from provider config)
    @property
    def provider_fee_percentage(self) -> float:
        """Get fee percentage from provider configuration."""
        try:
            from ..services.providers.registry import get_provider_registry
            registry = get_provider_registry()
            provider_instance = registry.get_provider(self.provider)
            if provider_instance:
                return float(provider_instance.get_fee_percentage(self.currency.code, self.currency.currency_type))
            return 0.005  # Default 0.5%
        except Exception:
            return 0.005  # Default fallback
    
    @property
    def provider_fixed_fee_usd(self) -> float:
        """Get fixed fee from provider configuration."""
        try:
            from ..services.providers.registry import get_provider_registry
            registry = get_provider_registry()
            provider_instance = registry.get_provider(self.provider)
            if provider_instance:
                return float(provider_instance.get_fixed_fee_usd(self.currency.code, self.currency.currency_type))
            return 0.0  # Default no fee
        except Exception:
            return 0.0  # Default fallback
    
    @property
    def provider_min_amount_usd(self) -> float:
        """Get minimum amount from provider configuration."""
        try:
            from ..services.providers.registry import get_provider_registry
            registry = get_provider_registry()
            provider_instance = registry.get_provider(self.provider)
            if provider_instance:
                return float(provider_instance.get_min_amount_usd(self.currency.code, self.currency.currency_type))
            return 0.000001  # Default minimum
        except Exception:
            return 0.000001  # Default fallback
    
    @property
    def provider_max_amount_usd(self) -> float:
        """Get maximum amount from provider configuration."""
        try:
            from ..services.providers.registry import get_provider_registry
            registry = get_provider_registry()
            provider_instance = registry.get_provider(self.provider)
            if provider_instance:
                return float(provider_instance.get_max_amount_usd(self.currency.code, self.currency.currency_type))
            return 1000000.0  # Default maximum
        except Exception:
            return 1000000.0  # Default fallback
    
    @property
    def provider_confirmation_blocks(self) -> int:
        """Get confirmation blocks from provider configuration."""
        try:
            from ..services.providers.registry import get_provider_registry
            registry = get_provider_registry()
            provider_instance = registry.get_provider(self.provider)
            if provider_instance and self.network:
                return provider_instance.get_confirmation_blocks(self.network.code)
            return 1  # Default
        except Exception:
            return 1  # Default fallback
    
    @property
    def provider_network_name(self) -> str:
        """Get network name from provider configuration."""
        try:
            from ..services.providers.registry import get_provider_registry
            registry = get_provider_registry()
            provider_instance = registry.get_provider(self.provider)
            if provider_instance and self.network:
                return provider_instance.get_network_name(self.network.code)
            return self.network.name if self.network else 'Unknown'
        except Exception:
            return self.network.name if self.network else 'Unknown'
