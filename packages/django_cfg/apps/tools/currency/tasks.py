"""
RQ tasks for currency rate updates.

Thin wrappers around services/update.py for RQ scheduler.
"""

from typing import Any, List, Optional


def update_all_rates(
    currencies: Optional[List[str]] = None,
    target_currency: Optional[str] = None,
) -> dict[str, Any]:
    """
    Update all exchange rates in CurrencyRate table.

    This is the main RQ task - runs hourly by default.

    Args:
        currencies: Currencies to update. None = all from Currency model.
        target_currency: Target currency for rates. None = from config.

    Returns:
        Dict with update statistics.
    """
    from .services import update_rates
    return update_rates(currencies, target_currency)


def refresh_rate(base: str, quote: str) -> dict[str, Any]:
    """
    Refresh single rate pair.

    Args:
        base: Base currency
        quote: Quote currency

    Returns:
        Rate info dict.
    """
    from .services import get_converter

    converter = get_converter()
    rate = converter.refresh_rate(base, quote)

    return {
        "pair": f"{base}/{quote}",
        "rate": str(rate.rate),
        "source": rate.source,
        "timestamp": rate.timestamp.isoformat(),
    }


def mark_stale_rates(max_age_hours: int = 24) -> dict[str, Any]:
    """
    Mark rates older than max_age as stale.

    Args:
        max_age_hours: Max age in hours before marking stale.

    Returns:
        Count of rates marked stale.
    """
    from django.utils import timezone
    from datetime import timedelta

    from django_cfg.modules.django_logging import get_logger
    from .models import CurrencyRate

    logger = get_logger(__name__)

    cutoff = timezone.now() - timedelta(hours=max_age_hours)
    count = CurrencyRate.objects.filter(
        updated_at__lt=cutoff,
        is_stale=False
    ).update(is_stale=True)

    logger.info(f"Marked {count} rates as stale (older than {max_age_hours}h)")

    return {
        "marked_stale": count,
        "cutoff": cutoff.isoformat(),
    }
