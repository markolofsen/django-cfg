"""
Database loader for populating currency data from external APIs.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
from dataclasses import dataclass

from pydantic import BaseModel, Field, validator
from cachetools import TTLCache

# CoinGecko API
from pycoingecko import CoinGeckoAPI
import yfinance as yf

logger = logging.getLogger(__name__)


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class CoinGeckoCoinInfo(BaseModel):
    """Single coin information from CoinGecko."""
    id: str = Field(description="CoinGecko coin ID")
    symbol: str = Field(description="Currency symbol (e.g., BTC)")
    name: str = Field(description="Full coin name")


class YFinanceCurrencyInfo(BaseModel):
    """Single fiat currency information."""
    code: str = Field(description="Currency code (e.g., USD)")
    name: str = Field(description="Full currency name")
    symbol: str = Field(default="", description="Currency symbol (e.g., $)")


class CurrencyRateInfo(BaseModel):
    """Currency rate information for database."""
    code: str = Field(description="Currency code")
    name: str = Field(description="Full currency name")
    symbol: str = Field(description="Currency symbol")
    currency_type: str = Field(description="fiat or crypto")
    decimal_places: int = Field(default=2, description="Decimal places")
    usd_rate: float = Field(description="Rate to USD")
    min_payment_amount: float = Field(default=1.0, description="Minimum payment amount")
    is_active: bool = Field(default=True, description="Is currency active")


class DatabaseLoaderConfig(BaseModel):
    """Configuration for database loader."""
    
    # Rate limiting
    coingecko_delay: float = Field(default=1.5, description="Delay between CoinGecko requests (seconds)")
    yfinance_delay: float = Field(default=0.5, description="Delay between YFinance requests (seconds)")
    max_requests_per_minute: int = Field(default=30, description="Max requests per minute")
    
    # Limits
    max_cryptocurrencies: int = Field(default=500, description="Max cryptocurrencies to load")
    max_fiat_currencies: int = Field(default=50, description="Max fiat currencies to load")
    
    # Filtering
    min_market_cap_usd: float = Field(default=1000000, description="Minimum market cap in USD")
    exclude_stablecoins: bool = Field(default=False, description="Exclude stablecoins")
    
    # Cache
    cache_ttl_hours: int = Field(default=24, description="Cache TTL in hours")


# ============================================================================
# RATE LIMITER
# ============================================================================

@dataclass
class RateLimiter:
    """Simple rate limiter to prevent API throttling."""
    
    def __init__(self, max_requests_per_minute: int = 30):
        self.max_requests = max_requests_per_minute
        self.requests = []
        self.last_request_time = 0.0
    
    def wait_if_needed(self, delay: float = 1.0):
        """Wait if necessary to respect rate limits."""
        current_time = time.time()
        
        # Remove old requests (older than 1 minute)
        self.requests = [req_time for req_time in self.requests 
                        if current_time - req_time < 60]
        
        # Check if we've hit the rate limit
        if len(self.requests) >= self.max_requests:
            sleep_time = 60 - (current_time - self.requests[0])
            if sleep_time > 0:
                logger.info(f"Rate limit reached, sleeping for {sleep_time:.2f}s")
                time.sleep(sleep_time)
        
        # Check minimum delay between requests
        time_since_last = current_time - self.last_request_time
        if time_since_last < delay:
            sleep_time = delay - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        # Record this request
        self.requests.append(time.time())
        self.last_request_time = time.time()


# ============================================================================
# DATABASE LOADER
# ============================================================================

class CurrencyDatabaseLoader:
    """
    Typed tool for loading currency data into database.
    
    Features:
    - Rate limiting to prevent API throttling
    - Configurable limits on number of currencies
    - Market cap filtering for cryptocurrencies
    - Caching to avoid repeated API calls
    - Type safety with Pydantic models
    """
    
    def __init__(self, config: DatabaseLoaderConfig = None):
        """Initialize the database loader."""
        self.config = config or DatabaseLoaderConfig()
        
        # Initialize API clients
        self.coingecko = CoinGeckoAPI()
        
        # Rate limiters
        self.coingecko_limiter = RateLimiter(self.config.max_requests_per_minute)
        self.yfinance_limiter = RateLimiter(self.config.max_requests_per_minute)
        
        # Cache
        cache_ttl = self.config.cache_ttl_hours * 3600
        self.crypto_cache = TTLCache(maxsize=10, ttl=cache_ttl)
        self.fiat_cache = TTLCache(maxsize=10, ttl=cache_ttl)
        
        logger.info(f"Initialized CurrencyDatabaseLoader with config: {self.config}")
    
    def get_cryptocurrency_list(self) -> List[CoinGeckoCoinInfo]:
        """
        Get list of cryptocurrencies from CoinGecko with filtering.
        
        Returns:
            List of cryptocurrency information
        """
        cache_key = "crypto_list"
        if cache_key in self.crypto_cache:
            logger.debug("Retrieved cryptocurrency list from cache")
            return self.crypto_cache[cache_key]
        
        logger.info("Fetching cryptocurrency list from CoinGecko...")
        
        try:
            # Get coins with market data for filtering
            self.coingecko_limiter.wait_if_needed(self.config.coingecko_delay)
            
            coins_markets = self.coingecko.get_coins_markets(
                vs_currency='usd',
                order='market_cap_desc',
                per_page=self.config.max_cryptocurrencies,
                page=1,
                sparkline=False
            )
            
            cryptocurrencies = []
            for coin in coins_markets:
                # Filter by market cap
                market_cap = coin.get('market_cap', 0) or 0
                if market_cap < self.config.min_market_cap_usd:
                    continue
                
                # Filter stablecoins if requested
                if self.config.exclude_stablecoins:
                    categories = coin.get('categories', []) or []
                    if any('stablecoin' in str(cat).lower() for cat in categories):
                        continue
                
                crypto_info = CoinGeckoCoinInfo(
                    id=coin['id'],
                    symbol=coin['symbol'].upper(),
                    name=coin['name']
                )
                cryptocurrencies.append(crypto_info)
            
            logger.info(f"Loaded {len(cryptocurrencies)} cryptocurrencies")
            self.crypto_cache[cache_key] = cryptocurrencies
            return cryptocurrencies
            
        except Exception as e:
            logger.error(f"Failed to fetch cryptocurrency list: {e}")
            raise
    
    def get_fiat_currency_list(self) -> List[YFinanceCurrencyInfo]:
        """
        Get list of fiat currencies.
        
        Returns:
            List of fiat currency information
        """
        cache_key = "fiat_list"
        if cache_key in self.fiat_cache:
            logger.debug("Retrieved fiat currency list from cache")
            return self.fiat_cache[cache_key]
        
        logger.info("Building fiat currency list...")
        
        # Major fiat currencies with their symbols
        fiat_currencies_data = [
            ("USD", "US Dollar", "$"),
            ("EUR", "Euro", "€"),
            ("GBP", "British Pound", "£"),
            ("JPY", "Japanese Yen", "¥"),
            ("CNY", "Chinese Yuan", "¥"),
            ("KRW", "South Korean Won", "₩"),
            ("CAD", "Canadian Dollar", "C$"),
            ("AUD", "Australian Dollar", "A$"),
            ("CHF", "Swiss Franc", "₣"),
            ("RUB", "Russian Ruble", "₽"),
            ("BRL", "Brazilian Real", "R$"),
            ("INR", "Indian Rupee", "₹"),
            ("MXN", "Mexican Peso", "$"),
            ("SGD", "Singapore Dollar", "S$"),
            ("HKD", "Hong Kong Dollar", "HK$"),
            ("SEK", "Swedish Krona", "kr"),
            ("NOK", "Norwegian Krone", "kr"),
            ("DKK", "Danish Krone", "kr"),
            ("PLN", "Polish Zloty", "zł"),
            ("CZK", "Czech Koruna", "Kč"),
            ("HUF", "Hungarian Forint", "Ft"),
            ("TRY", "Turkish Lira", "₺"),
            ("ZAR", "South African Rand", "R"),
            ("THB", "Thai Baht", "฿"),
            ("MYR", "Malaysian Ringgit", "RM"),
            ("PHP", "Philippine Peso", "₱"),
            ("IDR", "Indonesian Rupiah", "Rp"),
            ("VND", "Vietnamese Dong", "₫"),
            ("TWD", "Taiwan Dollar", "NT$"),
            ("NZD", "New Zealand Dollar", "NZ$")
        ]
        
        fiat_currencies = []
        for code, name, symbol in fiat_currencies_data[:self.config.max_fiat_currencies]:
            fiat_info = YFinanceCurrencyInfo(
                code=code,
                name=name,
                symbol=symbol
            )
            fiat_currencies.append(fiat_info)
        
        logger.info(f"Built list of {len(fiat_currencies)} fiat currencies")
        self.fiat_cache[cache_key] = fiat_currencies
        return fiat_currencies
    
    def get_currency_rates(self, currencies: List[str], vs_currency: str = "usd") -> Dict[str, float]:
        """
        Get current rates for multiple currencies.
        
        Args:
            currencies: List of currency codes/IDs
            vs_currency: Quote currency (default: usd)
            
        Returns:
            Dictionary mapping currency to its rate
        """
        if not currencies:
            return {}
        
        logger.info(f"Fetching rates for {len(currencies)} currencies vs {vs_currency}")
        
        try:
            # Split into chunks to avoid hitting API limits
            chunk_size = 50
            all_rates = {}
            
            for i in range(0, len(currencies), chunk_size):
                chunk = currencies[i:i + chunk_size]
                
                self.coingecko_limiter.wait_if_needed(self.config.coingecko_delay)
                
                # Join currency IDs for batch request
                ids_str = ','.join(chunk)
                
                price_data = self.coingecko.get_price(
                    ids=ids_str,
                    vs_currencies=vs_currency,
                    include_last_updated_at=True
                )
                
                # Extract rates
                for currency_id, data in price_data.items():
                    if vs_currency in data:
                        all_rates[currency_id] = float(data[vs_currency])
                
                logger.debug(f"Fetched rates for chunk {i//chunk_size + 1}")
            
            logger.info(f"Successfully fetched {len(all_rates)} currency rates")
            return all_rates
            
        except Exception as e:
            logger.error(f"Failed to fetch currency rates: {e}")
            raise
    
    def get_fiat_rate(self, base_currency: str, quote_currency: str = "USD") -> Optional[float]:
        """
        Get fiat currency rate using YFinance.
        
        Args:
            base_currency: Base currency code
            quote_currency: Quote currency code
            
        Returns:
            Exchange rate or None if not available
        """
        try:
            self.yfinance_limiter.wait_if_needed(self.config.yfinance_delay)
            
            if base_currency == quote_currency:
                return 1.0
            
            symbol = f"{base_currency}{quote_currency}=X"
            ticker = yf.Ticker(symbol)
            
            # Try to get current price
            info = ticker.info
            if 'regularMarketPrice' in info and info['regularMarketPrice']:
                return float(info['regularMarketPrice'])
            
            # Fallback to history
            hist = ticker.history(period="1d")
            if not hist.empty:
                return float(hist['Close'].iloc[-1])
            
            return None
            
        except Exception as e:
            logger.debug(f"Failed to get fiat rate for {base_currency}/{quote_currency}: {e}")
            return None
    
    def build_currency_database_data(self) -> List[CurrencyRateInfo]:
        """
        Build complete currency data for database insertion.
        
        Returns:
            List of currency rate information ready for database
        """
        logger.info("Building complete currency database data...")
        
        all_currencies = []
        
        # 1. Get fiat currencies
        logger.info("Processing fiat currencies...")
        fiat_currencies = self.get_fiat_currency_list()
        
        for fiat in fiat_currencies:
            # Get USD rate (skip USD itself)
            if fiat.code == "USD":
                usd_rate = 1.0
            else:
                usd_rate = self.get_fiat_rate(fiat.code, "USD")
                if usd_rate is None:
                    logger.warning(f"Could not get USD rate for {fiat.code}, skipping")
                    continue
            
            currency_info = CurrencyRateInfo(
                code=fiat.code,
                name=fiat.name,
                symbol=fiat.symbol,
                currency_type="fiat",
                decimal_places=2,
                usd_rate=usd_rate,
                min_payment_amount=1.0,
                is_active=True
            )
            all_currencies.append(currency_info)
            
            logger.debug(f"Added fiat currency: {fiat.code} = {usd_rate} USD")
        
        # 2. Get cryptocurrencies
        logger.info("Processing cryptocurrencies...")
        crypto_currencies = self.get_cryptocurrency_list()
        
        # Get rates in batches
        crypto_ids = [crypto.id for crypto in crypto_currencies]
        crypto_rates = self.get_currency_rates(crypto_ids, "usd")
        
        for crypto in crypto_currencies:
            if crypto.id not in crypto_rates:
                logger.warning(f"No USD rate found for {crypto.symbol}, skipping")
                continue
            
            usd_rate = crypto_rates[crypto.id]
            
            # Determine decimal places based on price
            if usd_rate >= 1:
                decimal_places = 2
            elif usd_rate >= 0.01:
                decimal_places = 4
            else:
                decimal_places = 8
            
            # Determine minimum payment amount
            if usd_rate >= 100:
                min_payment = 0.001
            elif usd_rate >= 1:
                min_payment = 0.01
            else:
                min_payment = 1.0
            
            currency_info = CurrencyRateInfo(
                code=crypto.symbol,
                name=crypto.name,
                symbol=crypto.symbol,  # Use symbol as symbol for crypto
                currency_type="crypto",
                decimal_places=decimal_places,
                usd_rate=usd_rate,
                min_payment_amount=min_payment,
                is_active=True
            )
            all_currencies.append(currency_info)
            
            logger.debug(f"Added cryptocurrency: {crypto.symbol} = {usd_rate} USD")
        
        logger.info(f"Built currency data for {len(all_currencies)} currencies "
                   f"({len(fiat_currencies)} fiat, {len(crypto_currencies)} crypto)")
        
        return all_currencies
    
    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about available currencies."""
        fiat_count = len(self.get_fiat_currency_list())
        crypto_count = len(self.get_cryptocurrency_list())
        
        return {
            "total_fiat_currencies": fiat_count,
            "total_cryptocurrencies": crypto_count,
            "total_currencies": fiat_count + crypto_count,
            "max_cryptocurrencies": self.config.max_cryptocurrencies,
            "max_fiat_currencies": self.config.max_fiat_currencies,
            "min_market_cap_usd": int(self.config.min_market_cap_usd)
        }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_database_loader(
    max_cryptocurrencies: int = 500,
    max_fiat_currencies: int = 50,
    min_market_cap_usd: float = 1000000,
    coingecko_delay: float = 1.5
) -> CurrencyDatabaseLoader:
    """
    Create a configured database loader.
    
    Args:
        max_cryptocurrencies: Maximum number of cryptocurrencies to load
        max_fiat_currencies: Maximum number of fiat currencies to load
        min_market_cap_usd: Minimum market cap for cryptocurrencies
        coingecko_delay: Delay between CoinGecko requests
        
    Returns:
        Configured CurrencyDatabaseLoader instance
    """
    config = DatabaseLoaderConfig(
        max_cryptocurrencies=max_cryptocurrencies,
        max_fiat_currencies=max_fiat_currencies,
        min_market_cap_usd=min_market_cap_usd,
        coingecko_delay=coingecko_delay
    )
    
    return CurrencyDatabaseLoader(config)


def load_currencies_to_database_format() -> List[Dict]:
    """
    Convenience function to get currency data in Django ORM format.
    
    Returns:
        List of dictionaries ready for bulk_create
    """
    loader = create_database_loader()
    currencies = loader.build_currency_database_data()
    
    # Convert to dictionary format for Django ORM
    currency_dicts = []
    for currency in currencies:
        currency_dict = {
            'code': currency.code,
            'name': currency.name,
            'symbol': currency.symbol,
            'currency_type': currency.currency_type,
            'decimal_places': currency.decimal_places,
            'usd_rate': currency.usd_rate,
            'min_payment_amount': currency.min_payment_amount,
            'is_active': currency.is_active,
            'rate_updated_at': datetime.now()
        }
        currency_dicts.append(currency_dict)
    
    return currency_dicts
