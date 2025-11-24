"""Decimal field configuration."""

from typing import Any, Dict, Literal, Optional

from pydantic import Field

from .base import FieldConfig


class DecimalField(FieldConfig):
    """
    Decimal number widget configuration.

    Examples:
        DecimalField(name="price", decimal_places=8)
        DecimalField(name="confidence", decimal_places=2, suffix="%")
        DecimalField(name="amount", decimal_places=2, prefix="$", show_sign=True)
    """

    ui_widget: Literal["decimal"] = "decimal"

    decimal_places: int = Field(2, description="Decimal places to display")
    prefix: Optional[str] = Field(None, description="Prefix symbol (e.g., '$')")
    suffix: Optional[str] = Field(None, description="Suffix symbol (e.g., '%', 'BTC')")
    show_sign: bool = Field(False, description="Show +/- sign")
    thousand_separator: bool = Field(True, description="Use thousand separator")

    def get_widget_config(self) -> Dict[str, Any]:
        """Extract decimal widget configuration."""
        config = super().get_widget_config()
        config['decimal_places'] = self.decimal_places
        if self.prefix is not None:
            config['prefix'] = self.prefix
        if self.suffix is not None:
            config['suffix'] = self.suffix
        config['show_sign'] = self.show_sign
        config['thousand_separator'] = self.thousand_separator
        return config
