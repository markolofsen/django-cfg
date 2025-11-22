"""Currency field configuration."""

from typing import Any, Dict, Literal

from pydantic import Field

from .base import FieldConfig


class CurrencyField(FieldConfig):
    """
    Currency/money widget configuration.

    Examples:
        CurrencyField(name="price", currency="USD", precision=2)
        CurrencyField(name="balance", currency="BTC", precision=8, show_sign=True)
    """

    ui_widget: Literal["currency"] = "currency"

    currency: str = Field("USD", description="Currency code (USD, EUR, BTC)")
    precision: int = Field(2, description="Decimal places")
    show_sign: bool = Field(False, description="Show +/- sign")
    thousand_separator: bool = Field(True, description="Use thousand separator")

    def get_widget_config(self) -> Dict[str, Any]:
        """Extract currency widget configuration."""
        config = super().get_widget_config()
        config['currency'] = self.currency
        config['decimal_places'] = self.precision
        config['show_sign'] = self.show_sign
        config['thousand_separator'] = self.thousand_separator
        return config
