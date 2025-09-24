"""
YFinance client for fiat currencies only.
"""

import logging
import yfinance as yf
from datetime import datetime
from typing import Set, Optional
from cachetools import TTLCache
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from ..core.models import Rate
from ..core.exceptions import RateFetchError

logger = logging.getLogger(__name__)


class YFinanceClient:
    """Client for fetching fiat currency rates from Yahoo Finance."""
    
    def __init__(self, cache_ttl: int = 3600):
        """Initialize YFinance client with TTL cache."""
        self._currency_cache = TTLCache(maxsize=1, ttl=cache_ttl)  # Cache currencies for 1 hour
        self._rate_cache = TTLCache(maxsize=1000, ttl=300)  # Cache rates for 5 minutes
    
    def fetch_rate(self, base: str, quote: str) -> Rate:
        """
        Fetch exchange rate from YFinance with caching.
        
        Args:
            base: Base currency code
            quote: Quote currency code
            
        Returns:
            Rate object with exchange rate data
            
        Raises:
            RateFetchError: If rate fetch fails
        """
        cache_key = f"{base}_{quote}"
        
        # Try cache first
        if cache_key in self._rate_cache:
            logger.debug(f"Retrieved rate {base}/{quote} from cache")
            return self._rate_cache[cache_key]
        
        try:
            rate = self._fetch_rate_with_retry(base, quote)
            
            # Cache the result
            self._rate_cache[cache_key] = rate
            
            return rate
            
        except Exception as e:
            logger.error(f"Failed to fetch rate for {base}/{quote}: {e}")
            raise RateFetchError(f"YFinance fetch failed: {e}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError, Exception)),
        reraise=True
    )
    def _fetch_rate_with_retry(self, base: str, quote: str) -> Rate:
        """
        Fetch rate with retry logic and exponential backoff.
        
        Args:
            base: Base currency code
            quote: Quote currency code
            
        Returns:
            Rate object with exchange rate data
        """
        symbol = self._build_symbol(base, quote)
        logger.debug(f"Fetching rate for {symbol}")
        
        ticker = yf.Ticker(symbol)
        
        # Try to get current price from info
        info = ticker.info
        if 'regularMarketPrice' in info and info['regularMarketPrice']:
            rate_value = float(info['regularMarketPrice'])
            logger.debug(f"Got rate from info: {rate_value}")
        else:
            # Fallback to history
            hist = ticker.history(period="1d")
            if hist.empty:
                raise RateFetchError(f"No data available for {symbol}")
            rate_value = float(hist['Close'].iloc[-1])
            logger.debug(f"Got rate from history: {rate_value}")
        
        return Rate(
            source="yfinance",
            base_currency=base,
            quote_currency=quote,
            rate=rate_value,
            timestamp=datetime.now()
        )
    
    def get_fiat_currencies(self) -> Set[str]:
        """Get all supported fiat currencies dynamically with caching."""
        cache_key = "fiat_currencies"
        
        # Try cache first
        if cache_key in self._currency_cache:
            logger.debug("Retrieved fiat currencies from cache")
            return self._currency_cache[cache_key]
        
        # Load currencies dynamically
        currencies = self._discover_fiat_currencies()
        
        # Cache the result
        self._currency_cache[cache_key] = currencies
        logger.info(f"Loaded and cached {len(currencies)} fiat currencies from YFinance")
        
        return currencies
    
    def _discover_fiat_currencies(self) -> Set[str]:
        """Discover available fiat currencies dynamically using YFinance with multithreading."""
        currencies = set()
        
        try:
            # Known major currencies to test efficiently
            test_currencies = [
                "USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "KRW", "RUB",
                "SGD", "HKD", "INR", "THB", "MYR", "PHP", "IDR", "VND", "BRL", "MXN", 
                "ZAR", "TRY", "PLN", "CZK", "HUF", "DKK", "SEK", "NOK", "NZD", "TWD"
            ]
            
            logger.debug(f"Testing {len(test_currencies)} currency pairs with multithreading...")
            
            @retry(
                stop=stop_after_attempt(2),
                wait=wait_exponential(multiplier=1, min=1, max=5),
                retry=retry_if_exception_type((ConnectionError, TimeoutError)),
                reraise=False  # Don't reraise for currency discovery
            )
            def test_currency(base_currency):
                """Test a single currency pair with retry logic."""
                try:
                    # Test against USD
                    symbol = f"{base_currency}USD=X" if base_currency != "USD" else "EURUSD=X"
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    
                    # If ticker has valid data, return the currencies
                    if info and 'symbol' in info:
                        result_currencies = set()
                        if base_currency != "USD":
                            result_currencies.add(base_currency)
                        result_currencies.add("USD")
                        logger.debug(f"Verified: {symbol}")
                        return result_currencies
                    return set()
                    
                except Exception as e:
                    logger.debug(f"Failed to verify {base_currency}: {e}")
                    return set()
            
            # Use ThreadPoolExecutor for parallel testing
            with ThreadPoolExecutor(max_workers=5) as executor:
                # Submit all tasks
                future_to_currency = {
                    executor.submit(test_currency, currency): currency 
                    for currency in test_currencies
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_currency):
                    try:
                        result = future.result(timeout=10)  # 10 second timeout per request
                        currencies.update(result)
                    except Exception as e:
                        currency = future_to_currency[future]
                        logger.debug(f"Future failed for {currency}: {e}")
                        
            logger.info(f"Discovered {len(currencies)} fiat currencies dynamically with multithreading")
            return currencies if currencies else {"USD", "EUR", "GBP", "JPY"}  # Fallback to major currencies
            
        except Exception as e:
            logger.warning(f"Failed to discover currencies dynamically: {e}")
            # Return minimal set as fallback
            return {"USD", "EUR", "GBP", "JPY", "CAD", "AUD"}

    def fetch_multiple_rates(self, pairs: list) -> dict:
        """
        Fetch multiple currency rates in parallel.
        
        Args:
            pairs: List of tuples (base, quote) to fetch
            
        Returns:
            Dictionary mapping "BASE_QUOTE" to Rate objects
        """
        results = {}
        
        def fetch_single_rate(pair):
            base, quote = pair
            try:
                rate = self.fetch_rate(base, quote)
                return f"{base}_{quote}", rate
            except Exception as e:
                logger.warning(f"Failed to fetch {base}/{quote}: {e}")
                return f"{base}_{quote}", None
        
        # Use ThreadPoolExecutor for parallel fetching
        with ThreadPoolExecutor(max_workers=8) as executor:  # YFinance can handle more parallel requests
            future_to_pair = {executor.submit(fetch_single_rate, pair): pair for pair in pairs}
            
            for future in as_completed(future_to_pair):
                try:
                    key, rate = future.result(timeout=15)
                    if rate:
                        results[key] = rate
                except Exception as e:
                    pair = future_to_pair[future]
                    logger.error(f"Failed to fetch rate for {pair}: {e}")
        
        logger.info(f"Successfully fetched {len(results)}/{len(pairs)} rates")
        return results
    
    def _build_symbol(self, base: str, quote: str) -> str:
        """Build YFinance symbol from currency pair."""
        base = base.upper()
        quote = quote.upper()
        
        # Only handle fiat pairs
        fiat_currencies = self.get_fiat_currencies()
        if base in fiat_currencies and quote in fiat_currencies:
            if base == quote:
                raise RateFetchError("Same currency conversion not needed")
            return f"{base}{quote}=X"
        
        raise RateFetchError(f"Unsupported fiat currency pair: {base}/{quote}")
    
    def supports_pair(self, base: str, quote: str) -> bool:
        """Check if fiat currency pair is supported."""
        base = base.upper()
        quote = quote.upper()
        
        fiat_currencies = self.get_fiat_currencies()
        return base in fiat_currencies and quote in fiat_currencies and base != quote
