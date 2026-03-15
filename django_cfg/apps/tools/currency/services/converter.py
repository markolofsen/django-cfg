"""
Currency converter with database-backed rate storage.

No separate cache - CurrencyRate model IS the cache.
"""

import logging
from decimal import Decimal
from typing import TYPE_CHECKING

from .exceptions import ConversionError, CurrencyNotFoundError
from .schemas import ConversionRequest, ConversionResult, Rate

if TYPE_CHECKING:
    from ..models import CurrencyRate

logger = logging.getLogger(__name__)

# Global converter instance
_converter: "CurrencyConverter | None" = None


def get_converter() -> "CurrencyConverter":
    """Get or create global converter instance."""
    global _converter
    if _converter is None:
        _converter = CurrencyConverter()
    return _converter


class CurrencyConverter:
    """
    Currency converter with intelligent routing.

    Uses CurrencyRate model for storage (no separate cache).
    """

    def __init__(self):
        """Initialize converter with rate providers."""
        from .clients import HybridCurrencyClient, CoinPaprikaClient

        self.hybrid = HybridCurrencyClient()
        self.coinpaprika = CoinPaprikaClient()

    def convert(
        self,
        amount: float | Decimal,
        from_currency: str,
        to_currency: str
    ) -> ConversionResult:
        """
        Convert amount from one currency to another.

        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code

        Returns:
            ConversionResult with converted amount and rate info
        """
        try:
            request = ConversionRequest(
                amount=float(amount),
                from_currency=from_currency.upper(),
                to_currency=to_currency.upper()
            )

            # Same currency check
            if request.from_currency == request.to_currency:
                rate = Rate(
                    source="internal",
                    base_currency=request.from_currency,
                    quote_currency=request.to_currency,
                    rate=1.0
                )
                return ConversionResult(
                    request=request,
                    result=float(amount),
                    rate=rate
                )

            # Get exchange rate
            rate = self.get_rate(request.from_currency, request.to_currency)

            # Calculate result
            result = float(amount) * rate.rate

            return ConversionResult(
                request=request,
                result=result,
                rate=rate
            )

        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            raise ConversionError(
                f"Failed to convert {amount} {from_currency} to {to_currency}: {e}"
            )

    def get_rate(self, base: str, quote: str) -> Rate:
        """
        Get exchange rate.

        Flow:
        1. Check CurrencyRate table
        2. If found and not expired, return it
        3. Otherwise fetch from provider
        4. Save to CurrencyRate table
        5. Return rate

        Args:
            base: Base currency code
            quote: Quote currency code

        Returns:
            Rate object
        """
        base, quote = base.upper(), quote.upper()

        # Check database first
        db_rate = self._get_db_rate(base, quote)
        if db_rate and not db_rate.is_expired:
            logger.debug(f"Using DB rate for {base}/{quote}")
            return Rate(
                source=db_rate.provider,
                base_currency=db_rate.base_currency,
                quote_currency=db_rate.quote_currency,
                rate=float(db_rate.rate),
                timestamp=db_rate.updated_at
            )

        # Fetch from provider
        rate = self._fetch_rate(base, quote)

        # Save to database
        self._save_rate(rate)

        return rate

    def refresh_rate(self, base: str, quote: str) -> Rate:
        """
        Force refresh rate from provider (bypass DB check).

        Args:
            base: Base currency code
            quote: Quote currency code

        Returns:
            Fresh Rate object
        """
        base, quote = base.upper(), quote.upper()
        rate = self._fetch_rate(base, quote)
        self._save_rate(rate)
        return rate

    def _get_db_rate(self, base: str, quote: str) -> "CurrencyRate | None":
        """Get rate from CurrencyRate model."""
        try:
            from ..models import CurrencyRate
            return CurrencyRate.get_rate(base, quote)
        except Exception as e:
            logger.debug(f"DB lookup failed: {e}")
            return None

    def _save_rate(self, rate: Rate) -> None:
        """Save rate to CurrencyRate model."""
        try:
            from ..models import CurrencyRate
            CurrencyRate.set_rate(
                rate.base_currency,
                rate.quote_currency,
                Decimal(str(rate.rate)),
                provider=rate.source
            )
        except Exception as e:
            logger.warning(f"Failed to save rate: {e}")

    def _fetch_rate(self, base: str, quote: str) -> Rate:
        """
        Fetch rate from providers.

        Tries in order:
        1. Hybrid client (fiat currencies)
        2. CoinPaprika (crypto)
        3. Indirect via USD
        """
        # Try Hybrid client first
        if self.hybrid.supports_pair(base, quote):
            try:
                rate = self.hybrid.fetch_rate(base, quote)
                return rate
            except Exception as e:
                logger.warning(f"Hybrid failed for {base}/{quote}: {e}")

        # Try CoinPaprika
        if self.coinpaprika.supports_pair(base, quote):
            try:
                rate = self.coinpaprika.fetch_rate(base, quote)
                return rate
            except Exception as e:
                logger.warning(f"CoinPaprika failed for {base}/{quote}: {e}")

        # Try indirect via USD
        if base != "USD" and quote != "USD":
            try:
                return self._indirect_conversion(base, quote)
            except Exception as e:
                logger.warning(f"Indirect conversion failed: {e}")

        raise CurrencyNotFoundError(f"No provider supports {base}/{quote}")

    def _indirect_conversion(self, base: str, quote: str) -> Rate:
        """Convert via USD bridge."""
        logger.debug(f"Indirect conversion {base} -> USD -> {quote}")

        base_usd = self._fetch_rate(base, "USD")
        usd_quote = self._fetch_rate("USD", quote)
        combined = base_usd.rate * usd_quote.rate

        return Rate(
            source=f"{base_usd.source}+{usd_quote.source}",
            base_currency=base,
            quote_currency=quote,
            rate=combined
        )
