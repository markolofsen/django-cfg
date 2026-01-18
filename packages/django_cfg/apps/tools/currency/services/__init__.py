"""Currency services."""

from .converter import CurrencyConverter, get_converter
from .schemas import Rate, ConversionRequest, ConversionResult
from .exceptions import (
    CurrencyError,
    CurrencyNotFoundError,
    RateFetchError,
    ConversionError,
)
from .update import (
    get_currency_config,
    should_update_rates,
    update_rates,
    update_rates_if_needed,
)

__all__ = [
    # Converter
    "CurrencyConverter",
    "get_converter",
    # Schemas
    "Rate",
    "ConversionRequest",
    "ConversionResult",
    # Exceptions
    "CurrencyError",
    "CurrencyNotFoundError",
    "RateFetchError",
    "ConversionError",
    # Update service
    "get_currency_config",
    "should_update_rates",
    "update_rates",
    "update_rates_if_needed",
]
