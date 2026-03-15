"""
Price Formatter - Smart currency formatting with abbreviations.

Provides intelligent price formatting with:
- Currency-specific symbols and positions
- Smart abbreviations (K, M, B for large numbers)
- Special handling for currencies like IDR, KRW
- Combining original + target currency display
"""

from decimal import Decimal
from typing import Optional, Union

Number = Union[int, float, Decimal]


class CurrencyConfig:
    """Configuration for a specific currency."""

    def __init__(
        self,
        symbol: str,
        position: str = "before",  # "before" or "after"
        decimals: int = 0,
        abbreviate: bool = False,
        abbreviate_threshold: int = 1_000,
        space_after_symbol: bool = False,
    ):
        self.symbol = symbol
        self.position = position
        self.decimals = decimals
        self.abbreviate = abbreviate
        self.abbreviate_threshold = abbreviate_threshold
        self.space_after_symbol = space_after_symbol


# Currency formatting configurations
CURRENCY_CONFIGS: dict[str, CurrencyConfig] = {
    # Major currencies
    "USD": CurrencyConfig(symbol="$", position="before", decimals=0, abbreviate=True),
    "EUR": CurrencyConfig(symbol="€", position="before", decimals=0, abbreviate=True),
    "GBP": CurrencyConfig(symbol="£", position="before", decimals=0, abbreviate=True),
    "JPY": CurrencyConfig(symbol="¥", position="before", decimals=0, abbreviate=True),
    "CNY": CurrencyConfig(symbol="¥", position="before", decimals=0, abbreviate=True),

    # Asian currencies with large denominations
    "IDR": CurrencyConfig(symbol="Rp", position="before", decimals=0, abbreviate=True, space_after_symbol=True),
    "KRW": CurrencyConfig(symbol="₩", position="before", decimals=0, abbreviate=True),
    "VND": CurrencyConfig(symbol="₫", position="after", decimals=0, abbreviate=True),

    # Other currencies
    "THB": CurrencyConfig(symbol="฿", position="before", decimals=0, abbreviate=True),
    "SGD": CurrencyConfig(symbol="S$", position="before", decimals=0, abbreviate=True),
    "MYR": CurrencyConfig(symbol="RM", position="before", decimals=0, abbreviate=True, space_after_symbol=True),
    "PHP": CurrencyConfig(symbol="₱", position="before", decimals=0, abbreviate=True),
    "INR": CurrencyConfig(symbol="₹", position="before", decimals=0, abbreviate=True),
    "AUD": CurrencyConfig(symbol="A$", position="before", decimals=0, abbreviate=True),
    "CAD": CurrencyConfig(symbol="C$", position="before", decimals=0, abbreviate=True),
    "CHF": CurrencyConfig(symbol="CHF", position="before", decimals=0, abbreviate=True, space_after_symbol=True),
    "RUB": CurrencyConfig(symbol="₽", position="after", decimals=0, abbreviate=True),
    "BRL": CurrencyConfig(symbol="R$", position="before", decimals=0, abbreviate=True),
    "MXN": CurrencyConfig(symbol="MX$", position="before", decimals=0, abbreviate=True),

    # Crypto
    "BTC": CurrencyConfig(symbol="₿", position="before", decimals=8, abbreviate=False),
    "ETH": CurrencyConfig(symbol="Ξ", position="before", decimals=4, abbreviate=False),
    "USDT": CurrencyConfig(symbol="₮", position="before", decimals=2, abbreviate=True),
}

# Default config for unknown currencies
DEFAULT_CONFIG = CurrencyConfig(symbol="", position="after", decimals=0, abbreviate=True, space_after_symbol=True)


class PriceFormatter:
    """
    Smart price formatter with currency-specific rules.

    Usage:
        formatter = PriceFormatter()

        # Basic formatting
        formatter.format(150_000_000, "IDR")  # "Rp 150M"
        formatter.format(9500, "USD")          # "$9,500"

        # Full display with both currencies
        formatter.format_full(
            amount=150_000_000,
            currency="IDR",
            target_amount=9500,
            target_currency="USD"
        )  # "$9,500 (Rp 150M)"

        # With suffix (for rentals)
        formatter.format(1500, "USD", suffix="/month")  # "$1,500/month"
    """

    # Abbreviation thresholds and suffixes
    ABBREVIATIONS = [
        (1_000_000_000, "B"),  # Billion
        (1_000_000, "M"),      # Million
        (1_000, "K"),          # Thousand
    ]

    def __init__(self, configs: Optional[dict[str, CurrencyConfig]] = None):
        """
        Initialize formatter with optional custom configs.

        Args:
            configs: Custom currency configurations (merged with defaults)
        """
        self.configs = {**CURRENCY_CONFIGS}
        if configs:
            self.configs.update(configs)

    def get_config(self, currency: str) -> CurrencyConfig:
        """Get configuration for currency code."""
        return self.configs.get(currency.upper(), DEFAULT_CONFIG)

    def abbreviate_number(self, amount: Number, config: CurrencyConfig) -> tuple[str, str]:
        """
        Abbreviate large number to K/M/B format.

        Returns:
            Tuple of (formatted_number, suffix)
        """
        amount = float(amount)

        if not config.abbreviate or abs(amount) < config.abbreviate_threshold:
            # No abbreviation - just format with commas
            if config.decimals == 0:
                return f"{int(amount):,}", ""
            return f"{amount:,.{config.decimals}f}", ""

        # Find appropriate abbreviation
        for threshold, suffix in self.ABBREVIATIONS:
            if abs(amount) >= threshold:
                abbreviated = amount / threshold
                # Use 1 decimal if needed, otherwise integer
                if abbreviated == int(abbreviated):
                    return f"{int(abbreviated):,}", suffix
                return f"{abbreviated:,.1f}", suffix

        # Below all thresholds
        if config.decimals == 0:
            return f"{int(amount):,}", ""
        return f"{amount:,.{config.decimals}f}", ""

    def format(
        self,
        amount: Optional[Number],
        currency: str,
        suffix: str = "",
        abbreviate: Optional[bool] = None,
    ) -> str:
        """
        Format price with currency symbol.

        Args:
            amount: The amount to format
            currency: Currency code (e.g., "USD", "IDR")
            suffix: Optional suffix (e.g., "/month", "/year")
            abbreviate: Override abbreviation setting (None = use config default)

        Returns:
            Formatted price string (e.g., "$9,500", "Rp 150M")
        """
        if amount is None:
            return "N/A"

        config = self.get_config(currency)

        # Override abbreviation if specified
        if abbreviate is not None:
            config = CurrencyConfig(
                symbol=config.symbol,
                position=config.position,
                decimals=config.decimals,
                abbreviate=abbreviate,
                abbreviate_threshold=config.abbreviate_threshold,
                space_after_symbol=config.space_after_symbol,
            )

        number_str, abbrev_suffix = self.abbreviate_number(amount, config)

        # Build the price string
        space = " " if config.space_after_symbol else ""
        symbol = config.symbol or currency

        if config.position == "before":
            price_str = f"{symbol}{space}{number_str}{abbrev_suffix}"
        else:
            price_str = f"{number_str}{abbrev_suffix}{space}{symbol}"

        return f"{price_str}{suffix}"

    def format_target(
        self,
        target_amount: Optional[Number],
        target_currency: str = "USD",
        suffix: str = "",
    ) -> str:
        """
        Format target (converted) price.

        Args:
            target_amount: Converted amount
            target_currency: Target currency code (default: USD)
            suffix: Optional suffix

        Returns:
            Formatted target price or "N/A"
        """
        return self.format(target_amount, target_currency, suffix=suffix)

    def format_full(
        self,
        amount: Optional[Number],
        currency: str,
        target_amount: Optional[Number] = None,
        target_currency: str = "USD",
        suffix: str = "",
        show_original: bool = True,
    ) -> str:
        """
        Format price with target currency and optional original.

        Shows target currency as primary, original in parentheses.

        Args:
            amount: Original amount
            currency: Original currency code
            target_amount: Converted amount (optional)
            target_currency: Target currency code (default: USD)
            suffix: Optional suffix (e.g., "/month")
            show_original: Whether to show original currency in parentheses

        Returns:
            Formatted full price (e.g., "$9,500 (Rp 150M)/month")
        """
        # If we have target amount and it's different currency
        if target_amount is not None and currency.upper() != target_currency.upper():
            target_str = self.format(target_amount, target_currency)

            if show_original and amount is not None:
                original_str = self.format(amount, currency)
                return f"{target_str} ({original_str}){suffix}"

            return f"{target_str}{suffix}"

        # Same currency or no target - just format original
        if amount is not None:
            return self.format(amount, currency, suffix=suffix)

        # Fallback to target if original not available
        if target_amount is not None:
            return self.format(target_amount, target_currency, suffix=suffix)

        return "N/A"


# Singleton instance for convenience
price_formatter = PriceFormatter()


# Convenience functions
def format_price(
    amount: Optional[Number],
    currency: str,
    suffix: str = "",
) -> str:
    """Format price with currency symbol."""
    return price_formatter.format(amount, currency, suffix=suffix)


def format_price_full(
    amount: Optional[Number],
    currency: str,
    target_amount: Optional[Number] = None,
    target_currency: str = "USD",
    suffix: str = "",
) -> str:
    """Format price with target currency and original in parentheses."""
    return price_formatter.format_full(
        amount=amount,
        currency=currency,
        target_amount=target_amount,
        target_currency=target_currency,
        suffix=suffix,
    )
