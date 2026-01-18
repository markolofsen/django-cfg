"""Currency exceptions."""


class CurrencyError(Exception):
    """Base currency exception."""
    pass


class CurrencyNotFoundError(CurrencyError):
    """Currency pair not supported."""
    pass


class RateFetchError(CurrencyError):
    """Failed to fetch rate from provider."""
    pass


class ConversionError(CurrencyError):
    """Conversion calculation failed."""
    pass
