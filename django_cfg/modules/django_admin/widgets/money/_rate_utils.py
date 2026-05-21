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
    Get a CurrencyRate-like view for the given base/quote pair.

    Returns a thin object exposing ``.rate`` and ``.updated_at`` so existing
    callers that read those two attributes keep working unchanged. The
    lookup goes through the process-level TTL cache in django_currency to
    avoid hammering the DB on every admin row render and to prevent
    pgbouncer idle-in-transaction leaks (see
    ``django_currency._rate_cache`` for the full story).

    Returns ``None`` if the Currency app is not installed or the rate is
    not found.
    """
    try:
        from django_cfg.modules.django_currency._rate_cache import get_cached_rate
    except ImportError:
        return None
    try:
        cached = get_cached_rate(base, quote)
    except Exception:
        return None
    if cached is None:
        return None
    return cached  # CachedRate is duck-compatible: has .rate + .updated_at
