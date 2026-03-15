"""
Currency rate update service.

Centralized logic for updating CurrencyRate from config.
Used by both apps.py (startup) and tasks.py (scheduled).
"""

from datetime import timedelta
from typing import Any, List, Optional

from django.utils import timezone

from django_cfg.modules.django_logging import get_logger

logger = get_logger(__name__)


def get_currency_config():
    """
    Get currency config from django-cfg.

    Returns:
        CurrencyConfig or None if not available.
    """
    try:
        from django_cfg.core.state import get_current_config
        config = get_current_config()
        if config and config.currency:
            return config.currency
    except Exception:
        pass
    return None


def should_update_rates() -> bool:
    """
    Check if rates need updating based on config and last update time.

    Returns:
        True if rates are stale or empty.
    """
    cfg = get_currency_config()
    if not cfg:
        return False

    if not cfg.enabled:
        return False

    from ..models import CurrencyRate

    # Check if we have recent rates
    interval = cfg.update_interval
    recent_cutoff = timezone.now() - timedelta(seconds=interval)

    has_recent_rates = CurrencyRate.objects.filter(
        updated_at__gte=recent_cutoff
    ).exists()

    return not has_recent_rates


def get_all_currency_codes() -> List[str]:
    """
    Get all active currency codes from Currency model.

    Returns:
        List of currency codes.
    """
    from ..models import Currency

    return list(
        Currency.objects.filter(is_active=True)
        .values_list("code", flat=True)
    )


def update_rates(
    currencies: Optional[List[str]] = None,
    target_currency: Optional[str] = None,
) -> dict[str, Any]:
    """
    Update exchange rates in CurrencyRate table using BATCH fetch.

    Fetches ALL rates in ONE API request (much faster than individual requests).
    Filters to only save currencies that are active in Currency model.

    Args:
        currencies: Currencies to update. None = all active from Currency model.
        target_currency: Target currency. None = from config (usually USD).

    Returns:
        Dict with update statistics.
    """
    from datetime import datetime
    from .clients.hybrid import HybridCurrencyClient
    from ..models import CurrencyRate

    # Get defaults from config
    cfg = get_currency_config()

    if currencies is None:
        currencies = get_all_currency_codes()

    if target_currency is None:
        target_currency = cfg.target_currency if cfg else "USD"

    # Filter out target currency
    currencies_to_update = set(c.upper() for c in currencies if c.upper() != target_currency.upper())

    if not currencies_to_update:
        return {
            "status": "success",
            "updated": 0,
            "failed": 0,
            "rates": [],
            "errors": [],
            "timestamp": datetime.now().isoformat(),
        }

    # BATCH FETCH: One API request gets ALL rates
    client = HybridCurrencyClient()
    updated = []
    failed = []

    try:
        logger.info(f"Batch fetching rates to {target_currency} (need {len(currencies_to_update)} currencies)...")

        # ONE request to get ALL rates
        all_rates = client.fetch_all_rates(target_currency)
        logger.info(f"Received {len(all_rates)} rates from API")

        # Filter and save only currencies we need
        for currency_code in currencies_to_update:
            if currency_code in all_rates:
                rate = all_rates[currency_code]
                try:
                    # Save to database
                    CurrencyRate.set_rate(
                        base=rate.base_currency,
                        quote=rate.quote_currency,
                        rate=rate.rate,
                        provider=rate.source,
                    )
                    updated.append({
                        "pair": f"{rate.base_currency}/{rate.quote_currency}",
                        "rate": str(rate.rate),
                        "source": rate.source,
                    })
                    logger.debug(f"Saved {rate.base_currency}/{rate.quote_currency}: {rate.rate}")
                except Exception as e:
                    failed.append({
                        "pair": f"{currency_code}/{target_currency}",
                        "error": f"DB save failed: {e}",
                    })
            else:
                failed.append({
                    "pair": f"{currency_code}/{target_currency}",
                    "error": "Not found in API response",
                })

    except Exception as e:
        logger.error(f"Batch fetch failed: {e}")
        # All currencies failed
        for currency_code in currencies_to_update:
            failed.append({
                "pair": f"{currency_code}/{target_currency}",
                "error": str(e),
            })

    result = {
        "status": "success" if not failed else ("partial" if updated else "failed"),
        "updated": len(updated),
        "failed": len(failed),
        "rates": updated,
        "errors": failed,
        "timestamp": datetime.now().isoformat(),
    }

    logger.info(f"Currency update: {len(updated)} updated, {len(failed)} failed (batch mode)")
    return result


def update_rates_if_needed() -> Optional[dict[str, Any]]:
    """
    Update rates only if needed (stale or empty).

    Used by apps.py for startup update.

    Returns:
        Update result dict or None if skipped.
    """
    cfg = get_currency_config()
    if not cfg:
        logger.debug("Currency config not available")
        return None

    if not cfg.update_on_startup:
        logger.debug("Currency update_on_startup disabled")
        return None

    if not should_update_rates():
        logger.debug("Currency rates are fresh, skipping update")
        return None

    logger.info("Running currency rates update...")
    result = update_rates()
    logger.info(f"Currency update complete: {result['updated']} rates updated")
    return result
