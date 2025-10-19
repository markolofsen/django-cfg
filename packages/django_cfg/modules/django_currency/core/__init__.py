"""
Core currency conversion functionality.
"""

from .converter import CurrencyConverter
from .exceptions import (
    CacheError,
    ConversionError,
    CurrencyError,
    CurrencyNotFoundError,
    RateFetchError,
)
from .models import ConversionRequest, ConversionResult, Rate

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
