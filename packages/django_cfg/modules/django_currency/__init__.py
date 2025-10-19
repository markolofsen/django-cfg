"""
Django Currency Module - Simple universal currency converter.

Provides seamless bidirectional conversion between fiat and cryptocurrency rates.
Uses YFinance for fiat/major crypto pairs and CoinGecko for broad crypto coverage.
"""

# Core functionality
# Clients
from .clients import CoinPaprikaClient, HybridCurrencyClient
from .core import (
    CacheError,
    ConversionError,
    ConversionRequest,
    ConversionResult,
    CurrencyConverter,
    CurrencyError,
    CurrencyNotFoundError,
    Rate,
    RateFetchError,
)

# Database tools
from .database import (
    CurrencyDatabaseLoader,
    DatabaseLoaderConfig,
    create_database_loader,
    load_currencies_to_database_format,
)

# Utilities
from .utils import CacheManager

# Shared global converter instance for caching efficiency
_global_converter = None

def _get_converter() -> CurrencyConverter:
    """Get or create shared converter instance."""
    global _global_converter
    if _global_converter is None:
        _global_converter = CurrencyConverter(cache_ttl=3600)  # 1 hour cache
    return _global_converter


# Simple public API
def convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
    """
    Convert currency amount.
    
    Args:
        amount: Amount to convert
        from_currency: Source currency code
        to_currency: Target currency code
        
    Returns:
        Converted amount
    """
    converter = _get_converter()
    result = converter.convert(amount, from_currency, to_currency)
    return result.result


def get_exchange_rate(base: str, quote: str) -> float:
    """
    Get exchange rate between currencies.
    
    Args:
        base: Base currency code
        quote: Quote currency code
        
    Returns:
        Exchange rate
    """
    converter = _get_converter()
    result = converter.convert(1.0, base, quote)
    return result.rate.rate


__all__ = [
    # Core converter and models
    "CurrencyConverter",
    "Rate",
    "ConversionRequest",
    "ConversionResult",

    # Exceptions
    "CurrencyError",
    "CurrencyNotFoundError",
    "RateFetchError",
    "ConversionError",
    "CacheError",

    # Utilities
    "CacheManager",

    # Clients
    "HybridCurrencyClient",
    "CoinPaprikaClient",

    # Database tools
    "CurrencyDatabaseLoader",
    "DatabaseLoaderConfig",
    "create_database_loader",
    "load_currencies_to_database_format",

    # Public API
    "convert_currency",
    "get_exchange_rate"
]
