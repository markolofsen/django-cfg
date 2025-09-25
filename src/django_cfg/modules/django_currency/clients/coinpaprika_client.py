"""
CoinPaprika client for crypto rates - much simpler and more reliable than CoinGecko.

CoinPaprika API provides all crypto rates in a single request without rate limits.
"""

import logging
import time
import requests
from datetime import datetime
from typing import Dict, Set, Optional, List
from cachetools import TTLCache

from ..core.models import Rate, CoinPaprikaTicker, CoinPaprikaTickersResponse
from ..core.exceptions import RateFetchError

logger = logging.getLogger(__name__)


class CoinPaprikaClient:
    """Client for fetching crypto rates from CoinPaprika API."""
    
    def __init__(self, cache_ttl: int = 600):
        """Initialize CoinPaprika client with TTL cache."""
        self.base_url = "https://api.coinpaprika.com/v1"
        self._rate_cache = TTLCache(maxsize=5000, ttl=cache_ttl)  # Cache rates for 10 minutes
        self._all_rates_cache = TTLCache(maxsize=1, ttl=300)  # Cache all rates for 5 minutes
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': 'django-cfg-currency-client/1.0',
            'Accept': 'application/json'
        })
    
    def fetch_rate(self, base: str, quote: str) -> Rate:
        """
        Fetch crypto exchange rate from CoinPaprika.
        
        Args:
            base: Base currency code (crypto)
            quote: Quote currency code (usually USD)
            
        Returns:
            Rate object with exchange rate data
            
        Raises:
            RateFetchError: If rate fetch fails
        """
        if quote.upper() != 'USD':
            raise RateFetchError(f"CoinPaprika only supports USD quotes, got {quote}")
        
        cache_key = f"{base.upper()}_{quote.upper()}"
        
        # Try cache first
        if cache_key in self._rate_cache:
            logger.debug(f"Retrieved rate {base}/{quote} from cache")
            return self._rate_cache[cache_key]
        
        try:
            # Get all rates and find our currency
            all_rates = self._fetch_all_rates()
            
            base_upper = base.upper()
            for ticker in all_rates:
                if ticker.symbol == base_upper:
                    price = ticker.quotes.USD.price
                    
                    # Parse ISO format: 2021-01-01T00:00:00Z
                    timestamp = datetime.fromisoformat(ticker.last_updated.replace('Z', '+00:00'))
                    
                    rate = Rate(
                        source="coinpaprika",
                        base_currency=base.upper(),
                        quote_currency="USD",
                        rate=float(price),
                        timestamp=timestamp
                    )
                    
                    # Cache the result
                    self._rate_cache[cache_key] = rate
                    
                    return rate
            
            raise RateFetchError(f"Currency {base} not found in CoinPaprika data")
            
        except Exception as e:
            logger.error(f"Failed to fetch rate for {base}/{quote}: {e}")
            raise RateFetchError(f"CoinPaprika fetch failed: {e}")
    
    def _fetch_all_tickers(self) -> Dict[str, dict]:
        """
        Fetch all tickers from CoinPaprika API.
        
        Returns:
            Dict with symbol as key and ticker data as value
        """
        cache_key = "all_tickers"
        if cache_key in self._all_rates_cache:
            logger.debug("Retrieved all tickers from CoinPaprika cache")
            return self._all_rates_cache[cache_key]

        try:
            response = requests.get(f"{self.base_url}/tickers")
            response.raise_for_status()
            tickers_data = response.json()
            
            # Process data into a more accessible format: {symbol: {id: ..., price: ...}}
            processed_tickers = {}
            for ticker in tickers_data:
                symbol = ticker['symbol'].upper()
                processed_tickers[symbol] = {
                    'id': ticker['id'],
                    'name': ticker['name'],
                    'price_usd': ticker['quotes']['USD']['price'] if 'USD' in ticker['quotes'] else None,
                    'last_updated': ticker['last_updated']
                }
            
            self._all_rates_cache[cache_key] = processed_tickers
            logger.info(f"Fetched and cached {len(processed_tickers)} tickers from CoinPaprika")
            return processed_tickers
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch all tickers from CoinPaprika: {e}")
            raise RateFetchError(f"CoinPaprika API error: {e}")

    def _fetch_all_rates(self) -> List[CoinPaprikaTicker]:
        """
        Fetch all cryptocurrency rates from CoinPaprika.
        
        Returns:
            List of CoinPaprikaTicker objects
        """
        cache_key = "all_rates"
        
        # Try cache first
        if cache_key in self._all_rates_cache:
            logger.debug("Retrieved all rates from cache")
            return self._all_rates_cache[cache_key]
        
        try:
            url = f"{self.base_url}/tickers"
            logger.debug(f"Fetching all rates from {url}")
            
            response = self._session.get(url, timeout=30)
            response.raise_for_status()
            
            raw_data = response.json()
            
            # Validate response using Pydantic model
            try:
                tickers_response = CoinPaprikaTickersResponse(raw_data)
                tickers = tickers_response.root
            except Exception as e:
                raise RateFetchError(f"Invalid CoinPaprika response format: {e}")
            
            # Cache the result
            self._all_rates_cache[cache_key] = tickers
            logger.info(f"Fetched {len(tickers)} cryptocurrencies from CoinPaprika")
            
            return tickers
            
        except requests.RequestException as e:
            logger.error(f"HTTP error fetching from CoinPaprika: {e}")
            raise RateFetchError(f"Failed to fetch data from CoinPaprika: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching from CoinPaprika: {e}")
            raise RateFetchError(f"CoinPaprika fetch failed: {e}")
    
    def get_supported_cryptocurrencies(self) -> Set[str]:
        """
        Get all supported cryptocurrency symbols.
        
        Returns:
            Set of supported crypto symbols
        """
        try:
            all_rates = self._fetch_all_rates()
            symbols = {ticker.symbol for ticker in all_rates}
            logger.debug(f"Found {len(symbols)} supported cryptocurrencies")
            return symbols
        except Exception as e:
            logger.error(f"Failed to get supported cryptocurrencies: {e}")
            return set()

    def get_all_supported_currencies(self) -> Dict[str, str]:
        """Get all supported cryptocurrencies from CoinPaprika."""
        all_tickers = self._fetch_all_tickers()
        return {symbol: data['name'] for symbol, data in all_tickers.items() if data['price_usd'] is not None}
    
    def supports_pair(self, base: str, quote: str) -> bool:
        """
        Check if a currency pair is supported.
        
        Args:
            base: Base currency code
            quote: Quote currency code
            
        Returns:
            True if supported, False otherwise
        """
        if quote.upper() != 'USD':
            return False
        
        supported_cryptos = self.get_supported_cryptocurrencies()
        return base.upper() in supported_cryptos
    
    def fetch_multiple_rates(self, currency_codes: List[str], quote: str = 'USD') -> Dict[str, Rate]:
        """
        Fetch multiple cryptocurrency rates efficiently.
        
        Args:
            currency_codes: List of crypto currency codes
            quote: Quote currency (default: USD)
            
        Returns:
            Dictionary mapping currency codes to Rate objects
        """
        if quote.upper() != 'USD':
            raise RateFetchError(f"CoinPaprika only supports USD quotes, got {quote}")
        
        results = {}
        
        try:
            # Fetch all rates once
            all_rates = self._fetch_all_rates()
            
            # Create lookup dictionary
            rates_by_symbol = {ticker.symbol: ticker for ticker in all_rates}
            
            # Process requested currencies
            for currency_code in currency_codes:
                currency_upper = currency_code.upper()
                
                if currency_upper in rates_by_symbol:
                    ticker = rates_by_symbol[currency_upper]
                    price = ticker.quotes.USD.price
                    
                    # Parse ISO format: 2021-01-01T00:00:00Z
                    timestamp = datetime.fromisoformat(ticker.last_updated.replace('Z', '+00:00'))
                    
                    rate = Rate(
                        source="coinpaprika",
                        base_currency=currency_upper,
                        quote_currency="USD",
                        rate=float(price),
                        timestamp=timestamp
                    )
                    
                    results[currency_upper] = rate
                    
                    # Cache individual rate
                    cache_key = f"{currency_upper}_USD"
                    self._rate_cache[cache_key] = rate
                else:
                    logger.warning(f"Currency {currency_code} not found in CoinPaprika data")
            
            logger.info(f"Successfully fetched {len(results)} rates from CoinPaprika")
            return results
            
        except Exception as e:
            logger.error(f"Failed to fetch multiple rates: {e}")
            raise RateFetchError(f"CoinPaprika batch fetch failed: {e}")
    
    def get_top_cryptocurrencies(self, limit: int = 100) -> List[Dict]:
        """
        Get top cryptocurrencies by market cap rank.
        
        Args:
            limit: Maximum number of currencies to return
            
        Returns:
            List of cryptocurrency data dictionaries
        """
        try:
            all_rates = self._fetch_all_rates()
            
            # Filter and sort by rank
            valid_tickers = [
                ticker for ticker in all_rates 
                if ticker.rank and ticker.quotes.USD.price
            ]
            
            # Sort by rank and limit
            top_tickers = sorted(valid_tickers, key=lambda x: x.rank)[:limit]
            
            logger.info(f"Retrieved top {len(top_tickers)} cryptocurrencies")
            return top_tickers
            
        except Exception as e:
            logger.error(f"Failed to get top cryptocurrencies: {e}")
            return []
