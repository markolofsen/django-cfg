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
from .currencies import (
    CURRENCIES,
    CURRENCY_CODES,
    FIAT_CODES,
    CRYPTO_CODES,
    get_currency_codes,
    clear_currency_cache,
    is_valid_currency,
    sync_currencies,
    sync_currencies_if_needed,
    sync_all,
    get_currency_stats,
    add_currency,
)
from .queryset import (
    get_conversion_rates,
    annotate_converted_price,
    filter_by_converted_price,
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
    # Currencies service
    "CURRENCIES",
    "CURRENCY_CODES",
    "FIAT_CODES",
    "CRYPTO_CODES",
    "get_currency_codes",
    "clear_currency_cache",
    "is_valid_currency",
    "sync_currencies",
    "sync_currencies_if_needed",
    "sync_all",
    "get_currency_stats",
    "add_currency",
    # Queryset helpers
    "get_conversion_rates",
    "annotate_converted_price",
    "filter_by_converted_price",
]
