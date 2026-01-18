"""Currency field configuration."""

from typing import Any, Dict, Literal

from pydantic import Field

from .base import FieldConfig


class CurrencyField(FieldConfig):
    """
    Currency/money widget configuration.

    Examples:
        # Fixed currency
        CurrencyField(name="price_usd", currency="USD")

        # Dynamic currency from model field
        CurrencyField(name="price", currency_field="currency")

        # With secondary value (e.g., USD equivalent)
        CurrencyField(
            name="price",
            currency_field="currency",
            secondary_field="price_usd",
            secondary_currency="USD",
        )
    """

    ui_widget: Literal["currency"] = "currency"

    # Fixed currency or dynamic from field
    currency: str | None = Field(None, description="Fixed currency code (USD, EUR, BTC)")
    currency_field: str | None = Field(None, description="Model field containing currency code")

    # Secondary value (e.g., USD equivalent)
    secondary_field: str | None = Field(None, description="Field with secondary currency value")
    secondary_currency: str = Field("USD", description="Secondary currency code")

    # Formatting
    precision: int = Field(2, description="Decimal places")
    show_sign: bool = Field(False, description="Show +/- sign")
    thousand_separator: bool = Field(True, description="Use thousand separator")

    def get_widget_config(self) -> Dict[str, Any]:
        """Extract currency widget configuration."""
        config = super().get_widget_config()
        config['currency'] = self.currency
        config['currency_field'] = self.currency_field
        config['secondary_field'] = self.secondary_field
        config['secondary_currency'] = self.secondary_currency
        config['decimal_places'] = self.precision
        config['show_sign'] = self.show_sign
        config['thousand_separator'] = self.thousand_separator
        return config
