"""
Django Currency Service for django_cfg.

Auto-configuring currency conversion service that integrates with DjangoConfig.
"""

from .service import DjangoCurrency, CurrencyError, CurrencyConfigError
from .converter import CurrencyConverter
from .cache import CurrencyCache

# Convenience functions
def convert_currency(
    amount: float, 
    from_currency: str, 
    to_currency: str,
    fail_silently: bool = False
) -> float:
    """Convert currency using auto-configured service."""
    currency = DjangoCurrency()
    return currency.convert(
        amount=amount,
        from_currency=from_currency,
        to_currency=to_currency,
        fail_silently=fail_silently
    )

def get_exchange_rate(from_currency: str, to_currency: str) -> float:
    """Get exchange rate using auto-configured service."""
    currency = DjangoCurrency()
    return currency.get_rate(from_currency, to_currency)

def get_available_currencies() -> set:
    """Get available currencies."""
    currency = DjangoCurrency()
    return currency.get_available_currencies()

# Export public API
__all__ = [
    'DjangoCurrency',
    'CurrencyConverter', 
    'CurrencyCache',
    'CurrencyError',
    'CurrencyConfigError',
    'convert_currency',
    'get_exchange_rate',
    'get_available_currencies'
]
