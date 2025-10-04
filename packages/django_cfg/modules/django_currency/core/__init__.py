"""
Core currency conversion functionality.
"""

from .models import (
    Rate,
    ConversionRequest,
    ConversionResult
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
    
    # Exceptions
    'CurrencyError',
    'CurrencyNotFoundError',
    'RateFetchError',
    'ConversionError',
    'CacheError',
    
    # Main converter
    'CurrencyConverter'
]
