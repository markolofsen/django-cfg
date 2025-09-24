"""
Custom exceptions for currency conversion.
"""


class CurrencyError(Exception):
    """Base currency conversion error."""
    pass


class CurrencyNotFoundError(CurrencyError):
    """Currency not supported by any provider."""
    pass


class RateFetchError(CurrencyError):
    """Failed to fetch exchange rate."""
    pass


class CacheError(CurrencyError):
    """Cache operation failed."""
    pass


class ConversionError(CurrencyError):
    """Currency conversion failed."""
    pass
