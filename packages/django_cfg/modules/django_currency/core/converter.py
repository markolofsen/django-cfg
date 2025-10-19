"""
Main currency converter with intelligent routing.
"""

import logging

from ..utils.cache import CacheManager
from .exceptions import ConversionError, CurrencyNotFoundError
from .models import ConversionRequest, ConversionResult, Rate

logger = logging.getLogger(__name__)


class CurrencyConverter:
    """Main currency converter with provider routing."""

    def __init__(self, cache_ttl: int = 300):
        """
        Initialize converter.

        Args:
            cache_ttl: Cache TTL in seconds
        """
        # Lazy import to avoid circular dependency
        from ..clients import CoinPaprikaClient, HybridCurrencyClient

        self.hybrid = HybridCurrencyClient(cache_ttl=cache_ttl)
        self.coinpaprika = CoinPaprikaClient(cache_ttl=cache_ttl)
        self.cache = CacheManager(ttl=cache_ttl)

    def convert(self, amount: float, from_currency: str, to_currency: str) -> ConversionResult:
        """
        Convert amount from one currency to another.
        
        Args:
            amount: Amount to convert
            from_currency: Source currency
            to_currency: Target currency
            
        Returns:
            ConversionResult with converted amount and rate info
            
        Raises:
            ConversionError: If conversion fails
        """
        try:
            # Validate input
            request = ConversionRequest(
                amount=amount,
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
                    result=amount,
                    rate=rate
                )

            # Get exchange rate
            rate = self._get_rate(request.from_currency, request.to_currency)

            # Calculate result
            result = amount * rate.rate

            return ConversionResult(
                request=request,
                result=result,
                rate=rate
            )

        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            raise ConversionError(f"Failed to convert {amount} {from_currency} to {to_currency}: {e}")

    def _get_rate(self, base: str, quote: str) -> Rate:
        """
        Get exchange rate using provider routing.
        
        Args:
            base: Base currency
            quote: Quote currency
            
        Returns:
            Rate object
            
        Raises:
            CurrencyNotFoundError: If no provider supports the pair
        """
        # Try cache first
        for source in ["hybrid", "coinpaprika"]:
            cached_rate = self.cache.get_rate(base, quote, source)
            if cached_rate:
                return cached_rate

        # Try Hybrid client first (multiple sources with fallback)
        if self.hybrid.supports_pair(base, quote):
            try:
                rate = self.hybrid.fetch_rate(base, quote)
                self.cache.set_rate(rate)
                return rate
            except Exception as e:
                logger.warning(f"Hybrid client failed for {base}/{quote}: {e}")

        # Try CoinPaprika next (excellent for crypto, no rate limits)
        if self.coinpaprika.supports_pair(base, quote):
            try:
                rate = self.coinpaprika.fetch_rate(base, quote)
                self.cache.set_rate(rate)
                return rate
            except Exception as e:
                logger.warning(f"CoinPaprika failed for {base}/{quote}: {e}")

        # Try indirect conversion via USD
        if base != "USD" and quote != "USD":
            try:
                return self._indirect_conversion(base, quote)
            except Exception as e:
                logger.warning(f"Indirect conversion failed for {base}/{quote}: {e}")

        raise CurrencyNotFoundError(f"No provider supports {base}/{quote}")

    def _indirect_conversion(self, base: str, quote: str) -> Rate:
        """
        Perform indirect conversion via USD.
        
        Args:
            base: Base currency
            quote: Quote currency
            
        Returns:
            Rate object with combined rate
        """
        logger.debug(f"Attempting indirect conversion {base} -> USD -> {quote}")

        # Get base/USD rate
        base_usd_rate = self._get_rate(base, "USD")

        # Get USD/quote rate
        usd_quote_rate = self._get_rate("USD", quote)

        # Calculate combined rate
        combined_rate = base_usd_rate.rate * usd_quote_rate.rate

        return Rate(
            source=f"{base_usd_rate.source}+{usd_quote_rate.source}",
            base_currency=base,
            quote_currency=quote,
            rate=combined_rate
        )

    def get_supported_currencies(self) -> dict:
        """Get list of supported currencies by provider."""
        return {
            "hybrid": self.hybrid.get_all_supported_currencies(),
            "coinpaprika": self.coinpaprika.get_all_supported_currencies()
        }
