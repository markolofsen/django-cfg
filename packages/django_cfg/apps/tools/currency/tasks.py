"""
RQ tasks for currency management.

Thin wrappers around services for RQ scheduler.
"""

from typing import Any, List, Optional


def sync_all(
    force_currencies: bool = False,
    force_rates: bool = False,
    target_currency: str = "USD",
) -> dict[str, Any]:
    """
    Sync currencies and rates in one call.

    Main task for scheduled execution.

    Args:
        force_currencies: Force currency sync even if enough exist
        force_rates: Force rate update even if fresh
        target_currency: Target currency for rates

    Returns:
        Combined result dict
    """
    from .services import sync_all as _sync_all
    return _sync_all(
        force_currencies=force_currencies,
        force_rates=force_rates,
        target_currency=target_currency,
    )


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
