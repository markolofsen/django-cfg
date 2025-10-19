"""
Database loader for populating currency data using Yahoo Finance + CoinPaprika.
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Optional

from cachetools import TTLCache
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class CoinPaprikaCoinInfo(BaseModel):
    """Single coin information from CoinPaprika."""
    id: str = Field(description="CoinPaprika coin ID")
    symbol: str = Field(description="Currency symbol (e.g., BTC)")
    name: str = Field(description="Full coin name")


class HybridCurrencyInfo(BaseModel):
    """Single currency information from hybrid client."""
    code: str = Field(description="Currency code (e.g., USD)")
    name: str = Field(description="Full currency name")
    symbol: str = Field(default="", description="Currency symbol (e.g., $)")
    currency_type: str = Field(description="Currency type (fiat, crypto, metal)")


class CurrencyRateInfo(BaseModel):
    """Currency rate information for database."""
    code: str = Field(description="Currency code")
    name: str = Field(description="Full currency name")
    symbol: str = Field(description="Currency symbol")
    currency_type: str = Field(description="fiat or crypto")
    decimal_places: int = Field(default=2, description="Decimal places")
    usd_rate: float = Field(description="Rate to USD")
    min_payment_amount: float = Field(default=1.0, description="Minimum payment amount")


class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self, max_requests_per_minute: int = 30):
        self.max_requests = max_requests_per_minute
        self.request_times = []

    def __call__(self):
        """Wait if necessary to respect rate limits."""
        now = time.time()

        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if now - t < 60]

        # If we're at the limit, wait
        if len(self.request_times) >= self.max_requests:
            sleep_time = 60 - (now - self.request_times[0]) + 1
            if sleep_time > 0:
                logger.debug(f"Rate limiting: sleeping for {sleep_time:.1f}s")
                time.sleep(sleep_time)

        self.request_times.append(now)


class DatabaseLoaderConfig(BaseModel):
    """Configuration for database loader."""

    yahoo_delay: float = Field(default=1.0, description="Delay between Yahoo requests")
    coinpaprika_delay: float = Field(default=0.5, description="Delay between CoinPaprika requests")
    max_requests_per_minute: int = Field(default=30, description="Max requests per minute")
    max_cryptocurrencies: int = Field(default=500, description="Max cryptocurrencies to load")
    max_fiat_currencies: int = Field(default=50, description="Max fiat currencies to load")
    min_market_cap_usd: float = Field(default=1000000, description="Minimum market cap for crypto")
    exclude_stablecoins: bool = Field(default=False, description="Exclude stablecoins")
    cache_ttl_hours: int = Field(default=24, description="Cache TTL in hours")


class CurrencyDatabaseLoader:
    """
    Database loader for populating currency data from Yahoo Finance and CoinPaprika.
    """

    def __init__(self, config: DatabaseLoaderConfig = None):
        """Initialize the database loader."""
        # Lazy import to avoid circular dependency
        from ..clients import CoinPaprikaClient, HybridCurrencyClient

        self.config = config or DatabaseLoaderConfig()

        # Initialize clients
        self.hybrid = HybridCurrencyClient(cache_ttl=self.config.cache_ttl_hours * 3600)
        self.coinpaprika = CoinPaprikaClient(cache_ttl=self.config.cache_ttl_hours * 3600)

        # Rate limiters
        self.yahoo_limiter = RateLimiter(self.config.max_requests_per_minute)
        self.coinpaprika_limiter = RateLimiter(self.config.max_requests_per_minute)

        # Caches
        cache_ttl = self.config.cache_ttl_hours * 3600
        self.crypto_cache = TTLCache(maxsize=1000, ttl=cache_ttl)
        self.fiat_cache = TTLCache(maxsize=100, ttl=cache_ttl)

        logger.info(f"Initialized CurrencyDatabaseLoader with config: {self.config}")

    def get_hybrid_currency_list(self) -> List[HybridCurrencyInfo]:
        """
        Get list of supported currencies from hybrid client.
        
        Returns:
            List of currency info objects
        """
        cache_key = "hybrid_currencies"

        if cache_key in self.fiat_cache:
            logger.debug("Retrieved hybrid currencies from cache")
            return self.fiat_cache[cache_key]

        # Get supported currencies from Hybrid client
        supported_currencies = self.hybrid.get_all_supported_currencies()

        # Convert to our format
        hybrid_currencies = []
        for code, name in supported_currencies.items():
            # Determine currency type based on code
            if code in ['BTC', 'ETH', 'BNB', 'XRP', 'ADA', 'SOL', 'DOT', 'MATIC',
                       'LTC', 'BCH', 'LINK', 'UNI', 'ATOM', 'XLM', 'VET', 'FIL',
                       'TRX', 'ETC', 'THETA', 'AAVE', 'MKR', 'COMP', 'SUSHI',
                       'USDT', 'USDC', 'BUSD', 'DAI', 'TUSD', 'USDP']:
                currency_type = "crypto"
            elif code in ['XAU', 'XAG', 'XPT', 'XPD']:
                currency_type = "metal"
            else:
                currency_type = "fiat"

            currency_info = HybridCurrencyInfo(
                code=code,
                name=name,
                symbol="$" if code == "USD" else "",  # Basic symbol mapping
                currency_type=currency_type
            )
            hybrid_currencies.append(currency_info)

        self.fiat_cache[cache_key] = hybrid_currencies
        logger.info(f"Loaded {len(hybrid_currencies)} currencies from hybrid client")

        return hybrid_currencies

    def get_cryptocurrency_list(self) -> List[CoinPaprikaCoinInfo]:
        """
        Get list of supported cryptocurrencies from CoinPaprika.
        
        Returns:
            List of cryptocurrency info objects
        """
        cache_key = "crypto_currencies"

        if cache_key in self.crypto_cache:
            logger.debug("Retrieved cryptocurrencies from cache")
            return self.crypto_cache[cache_key]

        try:
            # Get all tickers from CoinPaprika
            all_tickers = self.coinpaprika._fetch_all_tickers()

            crypto_currencies = []
            for symbol, data in all_tickers.items():
                # Skip if no price data
                if data.get('price_usd') is None:
                    continue

                # Apply market cap filter if needed
                # Note: CoinPaprika doesn't provide market cap in tickers endpoint
                # We'd need to use a different endpoint for that

                coin_info = CoinPaprikaCoinInfo(
                    id=data['id'],
                    symbol=symbol,
                    name=data['name']
                )
                crypto_currencies.append(coin_info)

                # Limit count
                if len(crypto_currencies) >= self.config.max_cryptocurrencies:
                    break

            self.crypto_cache[cache_key] = crypto_currencies
            logger.info(f"Loaded {len(crypto_currencies)} cryptocurrencies")

            return crypto_currencies

        except Exception as e:
            logger.error(f"Failed to get cryptocurrency list: {e}")
            return []

    def get_currency_rates(self, currency_ids: List[str], quote: str = 'usd') -> Dict[str, float]:
        """
        Get current rates for multiple cryptocurrencies.
        
        Args:
            currency_ids: List of currency symbols
            quote: Quote currency (usually 'usd')
            
        Returns:
            Dict mapping currency ID to rate
        """
        self.coinpaprika_limiter()

        try:
            rates = {}
            all_tickers = self.coinpaprika._fetch_all_tickers()

            for currency_id in currency_ids:
                if currency_id.upper() in all_tickers:
                    price = all_tickers[currency_id.upper()].get('price_usd')
                    if price is not None:
                        rates[currency_id] = price

            logger.debug(f"Retrieved rates for {len(rates)} currencies")
            return rates

        except Exception as e:
            logger.error(f"Failed to get currency rates: {e}")
            return {}

    def get_fiat_rate(self, base: str, quote: str) -> Optional[float]:
        """
        Get exchange rate for fiat currency pair.
        
        Args:
            base: Base currency code
            quote: Quote currency code
            
        Returns:
            Exchange rate or None if failed
        """
        # Handle same currency
        if base.upper() == quote.upper():
            return 1.0

        self.yahoo_limiter()

        try:
            rate_obj = self.hybrid.fetch_rate(base, quote)
            return rate_obj.rate
        except Exception as e:
            logger.debug(f"Failed to get fiat rate {base}/{quote}: {e}")
            return None

    def build_currency_database_data(self) -> List[CurrencyRateInfo]:
        """
        Build complete currency database data using hybrid client.
        
        Returns:
            List of currency rate info objects
        """
        currencies = []

        # Get currencies from hybrid client
        logger.info("Loading currencies from hybrid client...")
        hybrid_currencies = self.get_hybrid_currency_list()

        for currency in hybrid_currencies:
            # Get USD rate
            if currency.code == 'USD':
                usd_rate = 1.0
            else:
                usd_rate = self.get_fiat_rate(currency.code, 'USD')
                if usd_rate is None:
                    logger.warning(f"Could not get USD rate for {currency.code}")
                    continue

            # Set decimal places based on currency type and value
            if currency.currency_type == "fiat":
                decimal_places = 2
                min_payment = 1.0
            elif currency.currency_type == "crypto":
                if usd_rate >= 1:
                    decimal_places = 2
                elif usd_rate >= 0.01:
                    decimal_places = 4
                else:
                    decimal_places = 8
                min_payment = max(1.0 / usd_rate, 0.000001)
            else:  # metal
                decimal_places = 4
                min_payment = 0.001

            currency_info = CurrencyRateInfo(
                code=currency.code,
                name=currency.name,
                symbol=currency.symbol,
                currency_type=currency.currency_type,
                decimal_places=decimal_places,
                usd_rate=usd_rate,
                min_payment_amount=min_payment
            )
            currencies.append(currency_info)

        # Get additional cryptocurrencies from CoinPaprika (for extended crypto coverage)
        logger.info("Loading additional cryptocurrencies from CoinPaprika...")
        crypto_currencies = self.get_cryptocurrency_list()

        # Filter out cryptos that are already in hybrid client
        hybrid_crypto_codes = {c.code for c in hybrid_currencies if c.currency_type == "crypto"}

        if crypto_currencies:
            # Get rates for all cryptos
            crypto_symbols = [crypto.symbol for crypto in crypto_currencies
                            if crypto.symbol not in hybrid_crypto_codes]
            rates = self.get_currency_rates(crypto_symbols, 'usd')

            for crypto in crypto_currencies:
                # Skip if already covered by hybrid client
                if crypto.symbol in hybrid_crypto_codes:
                    continue

                if crypto.symbol in rates:
                    usd_rate = rates[crypto.symbol]

                    # Calculate appropriate decimal places based on USD value
                    if usd_rate >= 1:
                        decimal_places = 2
                    elif usd_rate >= 0.01:
                        decimal_places = 4
                    else:
                        decimal_places = 8

                    # Calculate minimum payment amount (roughly $1 worth)
                    min_payment = max(1.0 / usd_rate, 0.000001)

                    currency_info = CurrencyRateInfo(
                        code=crypto.symbol,
                        name=crypto.name,
                        symbol="",  # We don't have crypto symbols
                        currency_type="crypto",
                        decimal_places=decimal_places,
                        usd_rate=usd_rate,
                        min_payment_amount=min_payment
                    )
                    currencies.append(currency_info)

        logger.info(f"Built database data for {len(currencies)} currencies")
        return currencies

    def get_statistics(self) -> Dict[str, int]:
        """Get loader statistics."""
        hybrid_currencies = self.get_hybrid_currency_list()
        coinpaprika_cryptos = self.get_cryptocurrency_list()

        # Count by type from hybrid client
        fiat_count = len([c for c in hybrid_currencies if c.currency_type == "fiat"])
        hybrid_crypto_count = len([c for c in hybrid_currencies if c.currency_type == "crypto"])
        metal_count = len([c for c in hybrid_currencies if c.currency_type == "metal"])

        # Additional cryptos from CoinPaprika (excluding duplicates)
        hybrid_crypto_codes = {c.code for c in hybrid_currencies if c.currency_type == "crypto"}
        additional_crypto_count = len([c for c in coinpaprika_cryptos if c.symbol not in hybrid_crypto_codes])

        total_crypto_count = hybrid_crypto_count + additional_crypto_count

        return {
            'total_fiat_currencies': fiat_count,
            'total_cryptocurrencies': total_crypto_count,
            'total_metal_currencies': metal_count,
            'hybrid_crypto_currencies': hybrid_crypto_count,
            'coinpaprika_crypto_currencies': additional_crypto_count,
            'total_currencies': fiat_count + total_crypto_count + metal_count,
            'max_cryptocurrencies': self.config.max_cryptocurrencies,
            'max_fiat_currencies': self.config.max_fiat_currencies,
            'min_market_cap_usd': self.config.min_market_cap_usd
        }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_database_loader(
    max_cryptocurrencies: int = 500,
    max_fiat_currencies: int = 50,
    min_market_cap_usd: float = 1000000,
    yahoo_delay: float = 1.0,
    coinpaprika_delay: float = 0.5
) -> CurrencyDatabaseLoader:
    """
    Create a configured database loader.
    
    Args:
        max_cryptocurrencies: Maximum number of cryptocurrencies to load
        max_fiat_currencies: Maximum number of fiat currencies to load
        min_market_cap_usd: Minimum market cap for cryptocurrencies
        yahoo_delay: Delay between Yahoo Finance requests
        coinpaprika_delay: Delay between CoinPaprika requests
        
    Returns:
        Configured CurrencyDatabaseLoader instance
    """
    config = DatabaseLoaderConfig(
        max_cryptocurrencies=max_cryptocurrencies,
        max_fiat_currencies=max_fiat_currencies,
        min_market_cap_usd=min_market_cap_usd,
        yahoo_delay=yahoo_delay,
        coinpaprika_delay=coinpaprika_delay
    )
    return CurrencyDatabaseLoader(config)


def load_currencies_to_database_format() -> List[Dict]:
    """
    Load currencies and convert to database format.
    
    Returns:
        List of currency dictionaries ready for database insertion
    """
    loader = create_database_loader()
    currencies = loader.build_currency_database_data()

    # Convert to dict format
    result = []
    for currency in currencies:
        currency_dict = {
            'code': currency.code,
            'name': currency.name,
            'symbol': currency.symbol,
            'currency_type': currency.currency_type,
            'decimal_places': currency.decimal_places,
            'usd_rate': currency.usd_rate,
            'min_payment_amount': currency.min_payment_amount,
            'rate_updated_at': datetime.now()
        }
        result.append(currency_dict)

    return result
