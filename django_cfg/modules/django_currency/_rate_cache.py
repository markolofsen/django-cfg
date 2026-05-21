"""
Process-level TTL cache for CurrencyRate lookups.

Direct ORM access on every read of `obj.price_target` (and friends) causes
two production problems:

1. **Hot-path DB hits.** ``MoneyTargetDescriptor`` and its dependents
   (``_rounded`` / ``_display`` / ``_full_display``) call the ORM on every
   attribute read, so serializing a 100-row queryset fires 100 SELECTs
   against ``cfg_currency_rate``.
2. **idle-in-transaction leaks.** When the calling code is already inside
   a ``transaction.atomic()`` block on another database, the implicit
   transaction Django opens on ``default`` for the rate SELECT is not
   committed until the outer block exits. Under pgbouncer's transaction
   pool mode this pins the backend connection for the whole request and
   the per-(db, user) pool runs out — observed in production as
   ``psycopg_pool.PoolTimeout: couldn't get a connection`` together with
   long-lived ``idle in transaction`` rows in ``pg_stat_activity``.

This cache fixes both: each (base, quote) pair is looked up at most once
per :data:`CACHE_TTL_SECONDS`, and every DB hit is wrapped in
``transaction.atomic(using=...)`` so the connection commits and returns
to pgbouncer immediately.

Rates change roughly once per day; 5-minute staleness is acceptable.
Call :func:`clear_rate_cache` after the rate-update task to refresh
sooner — without this hook the worst-case staleness is just the TTL.
"""
from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# Rates change at most a few times a day; 5 minutes is a safe staleness
# budget and keeps the cache hot through bursty serializer traffic.
CACHE_TTL_SECONDS = 300


@dataclass(frozen=True)
class CachedRate:
    """Lightweight value object held in the cache.

    ``updated_at`` is kept ``Any`` so callers that don't need it pay no
    import cost for ``datetime``. It is the original
    ``CurrencyRate.updated_at`` value when present.
    """

    rate: Decimal
    updated_at: Any = None


# Cache shape: { (base_upper, quote_upper): (CachedRate | None, expires_at_monotonic) }
# ``None`` is cached as well — a negative result that costs the same as a
# hit and protects against pathological misses (e.g. an exotic currency
# the rates updater hasn't seen).
_cache: Dict[Tuple[str, str], Tuple[Optional[CachedRate], float]] = {}
_cache_lock = threading.Lock()


def _key(base: str, quote: str) -> Tuple[str, str]:
    return (base.upper(), quote.upper())


def _load_one(base: str, quote: str) -> Optional[CachedRate]:
    """Single rate SELECT, wrapped so the backend conn commits promptly."""
    try:
        from django.db import transaction
        from django_cfg.apps.tools.currency.models import CurrencyRate
    except ImportError:
        return None

    rate_db = CurrencyRate.objects.db or 'default'
    try:
        with transaction.atomic(using=rate_db):
            obj = (
                CurrencyRate.objects.using(rate_db)
                .filter(base_currency=base, quote_currency=quote)
                .only('rate', 'updated_at')
                .first()
            )
    except Exception:
        logger.debug("CurrencyRate lookup failed for %s->%s", base, quote, exc_info=True)
        return None

    if obj is None:
        return None
    return CachedRate(rate=obj.rate, updated_at=getattr(obj, 'updated_at', None))


def get_cached_rate(base: str, quote: str) -> Optional[CachedRate]:
    """Return the cached rate for ``base -> quote``, or ``None`` if absent.

    Identity pair (``base == quote``) returns ``Decimal("1")`` without a
    DB round-trip. Misses are cached as ``None`` for the TTL so a missing
    rate doesn't trigger a SELECT on every property access.
    """
    base_u = base.upper() if base else ''
    quote_u = quote.upper() if quote else ''
    if not base_u or not quote_u:
        return None
    if base_u == quote_u:
        return CachedRate(rate=Decimal('1'))

    key = (base_u, quote_u)
    now = time.monotonic()

    with _cache_lock:
        entry = _cache.get(key)
        if entry is not None and entry[1] > now:
            return entry[0]

    cached = _load_one(base_u, quote_u)
    with _cache_lock:
        _cache[key] = (cached, now + CACHE_TTL_SECONDS)
    return cached


def get_cached_rates_to(quote: str) -> Dict[str, CachedRate]:
    """Return all ``base -> quote`` rates as a dict keyed by base currency.

    Issues a single bulk SELECT and warms the per-pair cache as a side
    effect. Intended for callers that render a currency picker / table
    and want to avoid N+1 lookups.
    """
    try:
        from django.db import transaction
        from django_cfg.apps.tools.currency.models import CurrencyRate
    except ImportError:
        return {}

    quote_u = quote.upper()
    out: Dict[str, CachedRate] = {}
    rate_db = CurrencyRate.objects.db or 'default'
    now = time.monotonic()

    try:
        with transaction.atomic(using=rate_db):
            qs = (
                CurrencyRate.objects.using(rate_db)
                .filter(quote_currency=quote_u)
                .only('base_currency', 'rate', 'updated_at')
            )
            for obj in qs:
                cached = CachedRate(rate=obj.rate, updated_at=getattr(obj, 'updated_at', None))
                out[obj.base_currency] = cached
    except Exception:
        logger.debug("CurrencyRate bulk lookup failed for quote=%s", quote_u, exc_info=True)
        return out

    with _cache_lock:
        for base_u, cached in out.items():
            _cache[(base_u, quote_u)] = (cached, now + CACHE_TTL_SECONDS)
    return out


def clear_rate_cache() -> None:
    """Drop all cached rates.

    Call from the rate-updater task after a successful refresh so MoneyField
    descriptors and admin widgets pick up new rates without waiting for the
    TTL to expire.
    """
    with _cache_lock:
        _cache.clear()


__all__ = [
    "CACHE_TTL_SECONDS",
    "CachedRate",
    "get_cached_rate",
    "get_cached_rates_to",
    "clear_rate_cache",
]
