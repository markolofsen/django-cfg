"""
CoinGecko client for crypto rates only.
"""

import logging
import time
from datetime import datetime
from typing import Dict, Set, Optional
from cachetools import TTLCache
from pycoingecko import CoinGeckoAPI
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from ..core.models import Rate
from ..core.exceptions import RateFetchError

logger = logging.getLogger(__name__)


class CoinGeckoClient:
    """Client for fetching crypto rates from CoinGecko."""
    
    def __init__(self, cache_ttl: int = 3600, rate_limit_delay: float = 1.2):
        """Initialize CoinGecko client with TTL cache and rate limiting."""
        self.client = CoinGeckoAPI()
        self._crypto_cache = TTLCache(maxsize=2, ttl=cache_ttl)  # Cache crypto data for 1 hour
        self._rate_cache = TTLCache(maxsize=1000, ttl=600)  # Cache rates for 10 minutes
        self._last_request_time = 0.0
        self._rate_limit_delay = rate_limit_delay  # Delay between requests to avoid 429
    
    def fetch_rate(self, base: str, quote: str) -> Rate:
        """
        Fetch crypto exchange rate from CoinGecko with caching.
        
        Args:
            base: Base currency code (crypto)
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
            raise RateFetchError(f"CoinGecko fetch failed: {e}")

    @retry(
        stop=stop_after_attempt(4),  # More retries for CoinGecko due to rate limits
        wait=wait_exponential(multiplier=2, min=2, max=30),  # Longer waits for rate-limited API
        retry=retry_if_exception_type((ConnectionError, TimeoutError, Exception)),
        reraise=True
    )
    def _fetch_rate_with_retry(self, base: str, quote: str) -> Rate:
        """
        Fetch rate with retry logic and exponential backoff.
        
        Args:
            base: Base currency code (crypto)
            quote: Quote currency code
            
        Returns:
            Rate object with exchange rate data
        """
        base_id = self._get_crypto_id(base)
        quote_currency = quote.lower()
        
        vs_currencies = self.get_vs_currencies()
        if quote_currency not in vs_currencies:
            raise RateFetchError(f"Quote currency {quote} not supported by CoinGecko")
        
        logger.debug(f"Fetching rate for {base_id} vs {quote_currency}")
        
        # Fetch price from CoinGecko with rate limiting
        self._rate_limit()
        price_data = self.client.get_price(
            ids=base_id,
            vs_currencies=quote_currency,
            include_last_updated_at=True
        )
        
        if base_id not in price_data:
            raise RateFetchError(f"No data for {base}")
        
        rate_value = price_data[base_id][quote_currency]
        
        return Rate(
            source="coingecko",
            base_currency=base.upper(),
            quote_currency=quote.upper(),
            rate=float(rate_value),
            timestamp=datetime.now()
        )
    
    def get_crypto_ids(self) -> Dict[str, str]:
        """Get all supported cryptocurrencies dynamically with caching."""
        cache_key = "crypto_ids"
        
        # Try cache first
        if cache_key in self._crypto_cache:
            logger.debug("Retrieved crypto IDs from cache")
            return self._crypto_cache[cache_key]
        
        try:
            crypto_ids = self._get_coins_list_with_retry()
            
            # Cache the result
            self._crypto_cache[cache_key] = crypto_ids
            logger.info(f"Loaded and cached {len(crypto_ids)} cryptocurrencies from CoinGecko")
            
            return crypto_ids
            
        except Exception as e:
            logger.error(f"Failed to load cryptocurrencies: {e}")
            raise RateFetchError(f"Failed to load cryptocurrencies from CoinGecko: {e}")
    
    def get_vs_currencies(self) -> Set[str]:
        """Get all supported quote currencies dynamically with caching."""
        cache_key = "vs_currencies"
        
        # Try cache first
        if cache_key in self._crypto_cache:
            logger.debug("Retrieved vs_currencies from cache")
            return self._crypto_cache[cache_key]
        
        try:
            vs_currencies_set = self._get_vs_currencies_with_retry()
            
            # Cache the result
            self._crypto_cache[cache_key] = vs_currencies_set
            logger.info(f"Loaded and cached {len(vs_currencies_set)} vs_currencies from CoinGecko")
            
            return vs_currencies_set
            
        except Exception as e:
            logger.error(f"Failed to load vs_currencies: {e}")
            raise RateFetchError(f"Failed to load vs_currencies from CoinGecko: {e}")
    
    def _get_crypto_id(self, currency: str) -> str:
        """Get CoinGecko crypto ID from currency code."""
        currency = currency.upper()
        crypto_ids = self.get_crypto_ids()
        
        if currency in crypto_ids:
            return crypto_ids[currency]
        
        raise RateFetchError(f"Unknown cryptocurrency: {currency}")
    
    def _rate_limit(self):
        """Enforce rate limiting to prevent API throttling."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self._rate_limit_delay:
            sleep_time = self._rate_limit_delay - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self._last_request_time = time.time()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=15),
        retry=retry_if_exception_type((ConnectionError, TimeoutError, Exception)),
        reraise=True
    )
    def _get_coins_list_with_retry(self) -> Dict[str, str]:
        """Get coins list with retry logic."""
        self._rate_limit()
        coins_list = self.client.get_coins_list()
        crypto_ids = {}
        
        for coin in coins_list:
            symbol = coin['symbol'].upper()
            crypto_ids[symbol] = coin['id']
        
        return crypto_ids

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=15),
        retry=retry_if_exception_type((ConnectionError, TimeoutError, Exception)),
        reraise=True
    )
    def _get_vs_currencies_with_retry(self) -> Set[str]:
        """Get vs currencies with retry logic."""
        self._rate_limit()
        vs_currencies = self.client.get_supported_vs_currencies()
        return set(vs_currencies)

    def fetch_multiple_rates(self, pairs: list) -> Dict[str, Rate]:
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
        
        # Use ThreadPoolExecutor for parallel fetching with rate limiting
        with ThreadPoolExecutor(max_workers=3) as executor:  # Limited workers to respect rate limits
            future_to_pair = {executor.submit(fetch_single_rate, pair): pair for pair in pairs}
            
            for future in as_completed(future_to_pair):
                try:
                    key, rate = future.result(timeout=30)
                    if rate:
                        results[key] = rate
                except Exception as e:
                    pair = future_to_pair[future]
                    logger.error(f"Failed to fetch rate for {pair}: {e}")
        
        logger.info(f"Successfully fetched {len(results)}/{len(pairs)} rates")
        return results
    
    def supports_pair(self, base: str, quote: str) -> bool:
        """Check if crypto currency pair is supported."""
        try:
            # Base must be a crypto
            crypto_ids = self.get_crypto_ids()
            if base.upper() not in crypto_ids:
                return False
            
            # Quote must be a supported vs_currency
            vs_currencies = self.get_vs_currencies()
            return quote.lower() in vs_currencies
            
        except Exception:
            return False
