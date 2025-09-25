import logging
import requests
import time
from datetime import datetime
from typing import Dict, Set, Optional
from cachetools import TTLCache

from ..core.models import Rate, YahooFinanceResponse
from ..core.exceptions import RateFetchError

logger = logging.getLogger(__name__)


class YahooFinanceClient:
    """Simple Yahoo Finance client without yfinance dependency."""

    BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart"
    
    def __init__(self, cache_ttl: int = 3600):
        """Initialize Yahoo Finance client with TTL cache."""
        self._rate_cache = TTLCache(maxsize=500, ttl=cache_ttl)
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self._last_request_time = 0
        self._rate_limit_delay = 1.0  # 1 second between requests

    def _get_yahoo_symbol(self, base: str, quote: str) -> str:
        """Convert currency pair to Yahoo Finance symbol format."""
        # Yahoo uses format like EURUSD=X for forex pairs
        return f"{base}{quote}=X"

    def fetch_rate(self, base: str, quote: str) -> Rate:
        """
        Fetch forex rate from Yahoo Finance with caching.
        
        Args:
            base: Base currency code (e.g., EUR)
            quote: Quote currency code (e.g., USD)
            
        Returns:
            Rate object with exchange rate data
            
        Raises:
            RateFetchError: If rate fetch fails
        """
        base = base.upper()
        quote = quote.upper()
        cache_key = f"{base}_{quote}"

        # Try cache first
        if cache_key in self._rate_cache:
            logger.debug(f"Retrieved rate {base}/{quote} from Yahoo cache")
            return self._rate_cache[cache_key]

        symbol = self._get_yahoo_symbol(base, quote)
        
        # Rate limiting
        current_time = time.time()
        time_since_last_request = current_time - self._last_request_time
        if time_since_last_request < self._rate_limit_delay:
            sleep_time = self._rate_limit_delay - time_since_last_request
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        try:
            response = self._session.get(f"{self.BASE_URL}/{symbol}")
            self._last_request_time = time.time()
            response.raise_for_status()
            
            raw_data = response.json()
            
            # Validate response using Pydantic model
            try:
                yahoo_response = YahooFinanceResponse(**raw_data)
            except Exception as e:
                raise RateFetchError(f"Invalid Yahoo Finance response format: {e}")

            if not yahoo_response.chart.result:
                raise RateFetchError(f"No data returned for {symbol}")

            meta = yahoo_response.chart.result[0].meta
            rate_value = meta.regularMarketPrice
            timestamp = datetime.fromtimestamp(meta.regularMarketTime)
            
            rate = Rate(
                source="yahoo",
                base_currency=base,
                quote_currency=quote,
                rate=float(rate_value),
                timestamp=timestamp
            )
            
            self._rate_cache[cache_key] = rate
            logger.info(f"Fetched rate {base}/{quote} = {rate_value} from Yahoo Finance")
            return rate
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch rate from Yahoo Finance: {e}")
            raise RateFetchError(f"Yahoo Finance API error: {e}")
        except (KeyError, TypeError, ValueError) as e:
            logger.error(f"Failed to parse Yahoo Finance response: {e}")
            raise RateFetchError(f"Invalid response format: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching from Yahoo Finance: {e}")
            raise RateFetchError(f"Yahoo Finance fetch failed: {e}")

    def supports_pair(self, base: str, quote: str) -> bool:
        """
        Check if Yahoo Finance supports the given currency pair.
        
        Yahoo Finance primarily supports major forex pairs.
        """
        base = base.upper()
        quote = quote.upper()
        
        # Major currencies supported by Yahoo Finance
        major_currencies = {
            'USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD',
            'SEK', 'NOK', 'DKK', 'PLN', 'CZK', 'HUF', 'RUB', 'CNY',
            'INR', 'KRW', 'SGD', 'HKD', 'THB', 'MXN', 'BRL', 'ZAR',
            'TRY', 'ILS'
        }
        
        return base in major_currencies and quote in major_currencies

    def get_all_supported_currencies(self) -> Dict[str, str]:
        """Get all major currencies supported by Yahoo Finance."""
        return {
            'USD': 'US Dollar',
            'EUR': 'Euro',
            'GBP': 'British Pound',
            'JPY': 'Japanese Yen',
            'CHF': 'Swiss Franc',
            'CAD': 'Canadian Dollar',
            'AUD': 'Australian Dollar',
            'NZD': 'New Zealand Dollar',
            'SEK': 'Swedish Krona',
            'NOK': 'Norwegian Krone',
            'DKK': 'Danish Krone',
            'PLN': 'Polish Zloty',
            'CZK': 'Czech Koruna',
            'HUF': 'Hungarian Forint',
            'RUB': 'Russian Ruble',
            'CNY': 'Chinese Yuan',
            'INR': 'Indian Rupee',
            'KRW': 'South Korean Won',
            'SGD': 'Singapore Dollar',
            'HKD': 'Hong Kong Dollar',
            'THB': 'Thai Baht',
            'MXN': 'Mexican Peso',
            'BRL': 'Brazilian Real',
            'ZAR': 'South African Rand',
            'TRY': 'Turkish Lira',
            'ILS': 'Israeli Shekel'
        }
