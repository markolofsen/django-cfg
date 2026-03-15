"""
Currency rate utilities for MoneyFieldWidget.

Handles fetching currency choices and exchange rates from the Currency model.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Tuple

if TYPE_CHECKING:
    from django_cfg.apps.tools.currency.models import CurrencyRate

FALLBACK_CURRENCY_CHOICES: List[Tuple[str, str]] = [
    ("USD", "USD ($)"), ("EUR", "EUR (€)"), ("GBP", "GBP (£)"), ("JPY", "JPY (¥)"),
    ("CNY", "CNY (¥)"), ("KRW", "KRW (₩)"), ("RUB", "RUB (₽)"), ("CHF", "CHF (Fr)"),
    ("AUD", "AUD (A$)"), ("CAD", "CAD (C$)"), ("INR", "INR (₹)"), ("BRL", "BRL (R$)"),
    ("BTC", "BTC (₿)"), ("ETH", "ETH (Ξ)"),
]


def get_currency_choices() -> List[Tuple[str, str]]:
    """
    Get currency choices from the Currency model.

    Falls back to FALLBACK_CURRENCY_CHOICES when the model is empty or unavailable.
    """
    try:
        from django_cfg.apps.tools.currency.models import Currency
        currencies = Currency.objects.filter(is_active=True).order_by("code")
        if currencies.exists():
            return [(c.code, f"{c.code} ({c.symbol or c.name})") for c in currencies]
    except Exception:
        pass
    return FALLBACK_CURRENCY_CHOICES


def get_currency_rate(base: str, quote: str) -> Optional["CurrencyRate"]:
    """
    Get a CurrencyRate instance for the given base/quote pair.

    Returns None if the Currency app is not installed or the rate is not found.
    """
    try:
        from django_cfg.apps.tools.currency.models import CurrencyRate
        return CurrencyRate.objects.filter(
            base_currency=base.upper(),
            quote_currency=quote.upper(),
        ).first()
    except ImportError:
        return None
    except Exception:
        return None
