"""
Core currency conversion functionality.
"""

from .models import (
    Rate,
    ConversionRequest,
    ConversionResult,
    YFinanceCurrencies,
    CoinGeckoCurrencies,
    SupportedCurrencies
)

from .exceptions import (
    CurrencyError,
    CurrencyNotFoundError,
    RateFetchError,
    ConversionError,
    CacheError
)

from .converter import CurrencyConverter

__all__ = [
    # Models
    'Rate',
    'ConversionRequest', 
    'ConversionResult',
    'YFinanceCurrencies',
    'CoinGeckoCurrencies',
    'SupportedCurrencies',
    
    # Exceptions
    'CurrencyError',
    'CurrencyNotFoundError',
    'RateFetchError',
    'ConversionError',
    'CacheError',
    
    # Main converter
    'CurrencyConverter'
]
