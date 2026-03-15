"""
CoinPaprika Client - Cryptocurrency rate fetcher.

No API key required, no rate limits.
Supports top 100+ cryptocurrencies.
"""

import logging
from datetime import datetime
from typing import Dict, Set

import requests

from ..exceptions import RateFetchError
from ..schemas import Rate

logger = logging.getLogger(__name__)


class CoinPaprikaClient:
    """Cryptocurrency rate fetcher using CoinPaprika API."""

    BASE_URL = "https://api.coinpaprika.com/v1"

    # Common crypto symbols to CoinPaprika IDs
    SYMBOL_MAP = {
        "BTC": "btc-bitcoin",
        "ETH": "eth-ethereum",
        "BNB": "bnb-binance-coin",
        "SOL": "sol-solana",
        "XRP": "xrp-xrp",
        "ADA": "ada-cardano",
        "DOGE": "doge-dogecoin",
        "DOT": "dot-polkadot",
        "MATIC": "matic-polygon",
        "LTC": "ltc-litecoin",
        "USDT": "usdt-tether",
        "USDC": "usdc-usd-coin",
    }

    def __init__(self):
        """Initialize client."""
        self._session = requests.Session()
        self._tickers_cache: Dict[str, dict] = {}
        self._cache_time: float = 0

    def _fetch_all_tickers(self) -> Dict[str, dict]:
        """Fetch all tickers (cached for 5 minutes)."""
        import time

        # Return cache if fresh
        if self._tickers_cache and (time.time() - self._cache_time) < 300:
            return self._tickers_cache

        try:
            url = f"{self.BASE_URL}/tickers"
            response = self._session.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()

            # Build symbol -> ticker map
            self._tickers_cache = {}
            for ticker in data:
                symbol = ticker.get("symbol", "").upper()
                if symbol:
                    self._tickers_cache[symbol] = ticker

            self._cache_time = time.time()
            return self._tickers_cache

        except Exception as e:
            logger.warning(f"Failed to fetch CoinPaprika tickers: {e}")
            return self._tickers_cache or {}

    def fetch_rate(self, base: str, quote: str) -> Rate:
        """
        Fetch crypto rate.

        Note: CoinPaprika only provides USD quotes directly.
        For other quotes, we do indirect conversion.

        Args:
            base: Crypto symbol (BTC, ETH, etc.)
            quote: Quote currency (usually USD)

        Returns:
            Rate object
        """
        base, quote = base.upper(), quote.upper()

        # Get ticker for base currency
        tickers = self._fetch_all_tickers()

        if base not in tickers:
            raise RateFetchError(f"CoinPaprika: {base} not found")

        ticker = tickers[base]
        quotes = ticker.get("quotes", {})

        if "USD" not in quotes:
            raise RateFetchError(f"CoinPaprika: no USD quote for {base}")

        usd_price = quotes["USD"].get("price", 0)

        if quote == "USD":
            return Rate(
                source="coinpaprika",
                base_currency=base,
                quote_currency="USD",
                rate=usd_price,
                timestamp=datetime.now()
            )

        # For non-USD quotes, we need to convert
        # Get quote currency in USD terms
        if quote in tickers:
            # Both are crypto
            quote_usd_price = tickers[quote]["quotes"]["USD"]["price"]
            rate = usd_price / quote_usd_price
        else:
            # Quote is fiat - can't handle here
            raise RateFetchError(
                f"CoinPaprika: can't convert {base} to {quote} (use USD)"
            )

        return Rate(
            source="coinpaprika",
            base_currency=base,
            quote_currency=quote,
            rate=rate,
            timestamp=datetime.now()
        )

    def supports_pair(self, base: str, quote: str) -> bool:
        """Check if pair is supported (crypto to USD)."""
        base, quote = base.upper(), quote.upper()

        # We support crypto -> USD
        if quote == "USD":
            return base in self.SYMBOL_MAP or base in self._fetch_all_tickers()

        # Or crypto -> crypto
        tickers = self._fetch_all_tickers()
        return base in tickers and quote in tickers

    def get_supported_cryptos(self) -> Set[str]:
        """Get set of supported crypto symbols."""
        tickers = self._fetch_all_tickers()
        return set(tickers.keys())
