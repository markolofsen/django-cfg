"""
Django Currency Module.

Provides MoneyField and currency conversion utilities.
Uses CurrencyRate from django_cfg.apps.tools.currency for rate data.

MoneyField auto-creates:
    {field}_currency      - Currency code (CharField)
    {field}_target        - Converted amount (property)
    {field}_display       - Formatted original (e.g., "Rp 150M")
    {field}_target_display - Formatted target (e.g., "$9,500")
    {field}_full_display  - Combined (e.g., "$9,500 (Rp 150M)")
"""

from .fields import MoneyField, CurrencyField
from .admin import MoneyFieldAdminMixin
from .formatter import (
    PriceFormatter,
    price_formatter,
    format_price,
    format_price_full,
    CurrencyConfig,
    CURRENCY_CONFIGS,
)

__all__ = [
    # Fields
    "MoneyField",
    "CurrencyField",
    # Admin
    "MoneyFieldAdminMixin",
    # Formatter
    "PriceFormatter",
    "price_formatter",
    "format_price",
    "format_price_full",
    "CurrencyConfig",
    "CURRENCY_CONFIGS",
]
