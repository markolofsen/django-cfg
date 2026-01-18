"""Currency models."""

from decimal import Decimal
from typing import TYPE_CHECKING

from django.db import models
from django.db.models import QuerySet
from django.utils import timezone

# Database alias for currency tables (always use main DB)
CURRENCY_DB = "default"


class CurrencyQuerySet(QuerySet):
    """QuerySet that always uses the correct database."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._db = CURRENCY_DB


class CurrencyManager(models.Manager):
    """Manager that always uses the correct database."""

    def get_queryset(self) -> QuerySet:
        return CurrencyQuerySet(self.model, using=CURRENCY_DB)


class CurrencyRate(models.Model):
    """
    Cached exchange rate between currency pairs.

    Stores rates fetched from providers with TTL-based expiration.
    Single source of truth for all currency conversions.
    """

    objects: CurrencyManager = CurrencyManager()

    class Meta:
        app_label = "cfg_currency"
        db_table = "cfg_currency_rate"
        verbose_name = "Exchange Rate"
        verbose_name_plural = "Exchange Rates"
        unique_together = [("base_currency", "quote_currency")]
        ordering = ["base_currency", "quote_currency"]
        indexes = [
            models.Index(fields=["base_currency", "quote_currency"]),
            models.Index(fields=["updated_at"]),
        ]

    base_currency = models.CharField(
        max_length=10,
        db_index=True,
        help_text="Base currency code (e.g., KRW)"
    )
    quote_currency = models.CharField(
        max_length=10,
        db_index=True,
        help_text="Quote currency code (e.g., USD)"
    )
    rate = models.DecimalField(
        max_digits=24,
        decimal_places=12,
        help_text="Exchange rate (1 base = X quote)"
    )
    provider = models.CharField(
        max_length=50,
        default="hybrid",
        help_text="Rate provider source"
    )
    is_stale = models.BooleanField(
        default=False,
        help_text="Manually marked as needing refresh"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.base_currency}/{self.quote_currency}: {self.rate}"

    @property
    def is_expired(self) -> bool:
        """Check if rate is older than update interval."""
        age = (timezone.now() - self.updated_at).total_seconds()
        return age > self._get_update_interval()

    @staticmethod
    def _get_update_interval() -> int:
        """Get update interval from config."""
        try:
            from django_cfg.core.state import get_current_config
            config = get_current_config()
            if config and config.currency:
                return config.currency.update_interval
        except Exception:
            pass
        return 3600  # Default 1 hour

    @property
    def age_seconds(self) -> float:
        """Get rate age in seconds."""
        return (timezone.now() - self.updated_at).total_seconds()

    @classmethod
    def get_rate(cls, base: str, quote: str) -> "CurrencyRate | None":
        """
        Get exchange rate for currency pair.

        Args:
            base: Base currency code
            quote: Quote currency code

        Returns:
            CurrencyRate instance or None if not found
        """
        return cls.objects.filter(
            base_currency=base.upper(),
            quote_currency=quote.upper()
        ).first()

    @classmethod
    def get_rate_value(cls, base: str, quote: str) -> Decimal | None:
        """
        Get rate value as Decimal.

        Args:
            base: Base currency code
            quote: Quote currency code

        Returns:
            Rate as Decimal or None if not found
        """
        rate = cls.get_rate(base, quote)
        return rate.rate if rate else None

    @classmethod
    def set_rate(
        cls,
        base: str,
        quote: str,
        rate: Decimal | float,
        provider: str = "hybrid"
    ) -> "CurrencyRate":
        """
        Set or update exchange rate.

        Args:
            base: Base currency code
            quote: Quote currency code
            rate: Exchange rate value
            provider: Rate provider name

        Returns:
            Created or updated CurrencyRate instance
        """
        obj, _ = cls.objects.update_or_create(
            base_currency=base.upper(),
            quote_currency=quote.upper(),
            defaults={
                "rate": Decimal(str(rate)),
                "provider": provider,
                "is_stale": False,
            }
        )
        return obj

    @classmethod
    def mark_stale(cls, base: str | None = None, quote: str | None = None) -> int:
        """
        Mark rates as stale.

        Args:
            base: Filter by base currency (optional)
            quote: Filter by quote currency (optional)

        Returns:
            Number of rates marked as stale
        """
        qs = cls.objects.all()
        if base:
            qs = qs.filter(base_currency=base.upper())
        if quote:
            qs = qs.filter(quote_currency=quote.upper())
        return qs.update(is_stale=True)


class Currency(models.Model):
    """
    Currency metadata (optional).

    Stores information about supported currencies for admin display.
    """

    objects: CurrencyManager = CurrencyManager()

    class CurrencyType(models.TextChoices):
        FIAT = "fiat", "Fiat"
        CRYPTO = "crypto", "Crypto"

    class Meta:
        app_label = "cfg_currency"
        db_table = "cfg_currency"
        verbose_name = "Currency"
        verbose_name_plural = "Currencies"
        ordering = ["code"]

    code = models.CharField(
        max_length=10,
        unique=True,
        db_index=True,
        help_text="Currency code (e.g., USD, BTC)"
    )
    name = models.CharField(
        max_length=100,
        help_text="Currency name"
    )
    symbol = models.CharField(
        max_length=10,
        blank=True,
        default="",
        help_text="Currency symbol (e.g., $, €)"
    )
    currency_type = models.CharField(
        max_length=10,
        choices=CurrencyType.choices,
        default=CurrencyType.FIAT,
        help_text="Fiat or cryptocurrency"
    )
    decimals = models.PositiveSmallIntegerField(
        default=2,
        help_text="Decimal places for display"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether currency is available for conversion"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} ({self.name})"

    @property
    def display_name(self) -> str:
        """Get formatted display name."""
        if self.symbol:
            return f"{self.code} ({self.symbol} {self.name})"
        return f"{self.code} ({self.name})"
