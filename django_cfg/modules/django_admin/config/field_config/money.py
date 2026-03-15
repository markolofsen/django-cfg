"""
MoneyField display configuration for django_currency.MoneyField.

Provides compact display of all money-related fields:
- Primary amount with source currency
- Converted amount in target currency
- Exchange rate and update timestamp
"""

from typing import Any, Dict, Literal, Optional

from pydantic import Field

from .base import FieldConfig


class MoneyFieldDisplay(FieldConfig):
    """
    Compact display for MoneyField (from django_currency module).

    Automatically shows:
    - Original amount: "₩15,700,000"
    - Converted amount: "→ $10,645.05"
    - Rate info: "Rate: 0.000678 • 2h ago"

    Example:
        MoneyFieldDisplay(
            name="price",
            title="Price",
            # Auto-detects: price_currency, price_target, price_rate, price_rate_at
        )

        # Or explicit field names:
        MoneyFieldDisplay(
            name="price",
            currency_field="price_currency",
            target_field="price_target",
            target_currency="USD",
            rate_field="price_rate",
            rate_at_field="price_rate_at",
        )
    """

    ui_widget: Literal["money_field"] = "money_field"

    # Source currency
    currency_field: Optional[str] = Field(
        None,
        description="Field containing source currency code. Auto: {name}_currency"
    )
    default_currency: str = Field("USD", description="Default currency if not set")

    # Target/converted amount
    target_field: Optional[str] = Field(
        None,
        description="Field with converted amount. Auto: {name}_target"
    )
    target_currency: str = Field("USD", description="Target currency code")

    # Exchange rate info
    rate_field: Optional[str] = Field(
        None,
        description="Field with exchange rate. Auto: {name}_rate"
    )
    rate_at_field: Optional[str] = Field(
        None,
        description="Field with rate timestamp. Auto: {name}_rate_at"
    )

    # Display options
    show_rate: bool = Field(True, description="Show rate info line")
    precision: int = Field(2, description="Decimal places for amounts")
    compact: bool = Field(True, description="Use compact single-line display")

    # Currency symbols map
    currency_symbols: Dict[str, str] = Field(
        default_factory=lambda: {
            "USD": "$",
            "EUR": "€",
            "GBP": "£",
            "JPY": "¥",
            "KRW": "₩",
            "CNY": "¥",
            "RUB": "₽",
            "BTC": "₿",
            "ETH": "Ξ",
        }
    )

    def get_field_names(self) -> Dict[str, str]:
        """Get all related field names (auto-detect from base name)."""
        base = self.name
        return {
            "amount": base,
            "currency": self.currency_field or f"{base}_currency",
            "target": self.target_field or f"{base}_target",
            "rate": self.rate_field or f"{base}_rate",
            "rate_at": self.rate_at_field or f"{base}_rate_at",
        }

    def get_currency_symbol(self, currency_code: str) -> str:
        """Get currency symbol for code."""
        return self.currency_symbols.get(currency_code.upper(), currency_code)

    def get_widget_config(self) -> Dict[str, Any]:
        """Extract widget configuration."""
        config = super().get_widget_config()
        config.update({
            "field_names": self.get_field_names(),
            "target_currency": self.target_currency,
            "default_currency": self.default_currency,
            "show_rate": self.show_rate,
            "precision": self.precision,
            "compact": self.compact,
            "currency_symbols": self.currency_symbols,
        })
        return config
