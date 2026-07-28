"""Site resolution.

The gap this closes: before it, an AnalyticsSite row had to be created by hand,
and until someone did, /collect/ answered 202 {"accepted": 0} for every event.
That failure mode is indistinguishable from success — the worst kind for
analytics, where nobody notices until they open a dashboard weeks later and it
is empty.

Single source of truth: ``security_domains`` already declares which domains
belong to this project (it drives ALLOWED_HOSTS, CORS and CSRF). Analytics
derives from it rather than asking the operator to restate the same fact in a
second place, where the two would inevitably drift.

A domain NOT in security_domains is still rejected — that is the tenant
boundary, and auto-creating a row for any domain that POSTs at us would let a
stranger's traffic (or a spammer's) into the database.
"""

from __future__ import annotations

import logging
from urllib.parse import urlparse

from django.db import DatabaseError, IntegrityError, transaction

from ..models import AnalyticsProperty, AnalyticsSite

logger = logging.getLogger("django_cfg.analytics")


def _trusted_domains() -> set[str]:
    # get_current_config, NOT get_config — the latter does not exist. Importing
    # it inside a `try: ... except Exception` (as apps/tools/geo/apps.py:41 still
    # does) turns the typo into a silent fallback that is never noticed.
    from django_cfg.core import get_current_config

    config = get_current_config()
    if config is None:  # not running under DjangoConfig
        return set()

    domains: set[str] = set()
    for raw in getattr(config, "security_domains", None) or []:
        domain = raw.strip().lower().lstrip("*.")
        if domain:
            domains.add(domain)
    return domains


def _default_timezone() -> str:
    from django.conf import settings

    return getattr(settings, "TIME_ZONE", "UTC") or "UTC"


def claimed_domain(request, fallback: str = "") -> str:
    """The domain this request ACTUALLY came from.

    The client sends a ``site`` in the request body, but that field is
    attacker-controlled: anyone can POST ``{"site": "yourdomain.com"}`` from
    anywhere and pollute your analytics with events that never happened. The body
    cannot be the source of truth.

    ``Origin`` and ``Referer`` can: they are forbidden headers, so page
    JavaScript cannot forge them — the browser sets them from the document's real
    origin. When one is present it WINS over the body.

    A request with neither (a server-side call, curl, a stripped referrer policy)
    falls back to the body — which is fine, because the domain must still be in
    ``security_domains`` to resolve at all.
    """
    origin = request.META.get("HTTP_ORIGIN", "")
    referer = request.META.get("HTTP_REFERER", "")

    for raw in (origin, referer):
        if not raw:
            continue
        try:
            host = (urlparse(raw).hostname or "").strip().lower()
        except ValueError:
            continue
        if host:
            return host

    return (fallback or "").strip().lower()


def resolve_site(domain: str) -> AnalyticsSite | None:
    """Return the AnalyticsSite for ``domain``, provisioning it when trusted.

    Returns None for an unknown domain — the caller drops the batch.

    ``domain`` must come from ``claimed_domain()``, not straight from the request
    body. See that function for why.
    """
    domain = (domain or "").strip().lower()
    if not domain:
        return None

    site = AnalyticsSite.objects.filter(domain=domain).first()
    if site is not None:
        # An explicitly deactivated site stays off. That is an operator decision.
        if not site.is_active:
            return None
        return ensure_property(site)

    if domain not in _trusted_domains():
        logger.warning(
            "Analytics: dropping events for unknown domain %r. Add it to "
            "security_domains, or create an AnalyticsSite for it in the admin.",
            domain,
        )
        return None

    try:
        with transaction.atomic():
            site = AnalyticsSite.objects.create(
                domain=domain,
                name=domain,
                timezone=_default_timezone(),
            )
    except IntegrityError:
        # Two concurrent first-hits raced. The unique constraint on `domain`
        # settles it; the loser just re-reads.
        return AnalyticsSite.objects.filter(domain=domain).first()

    logger.info("Analytics: auto-registered site %r from security_domains", domain)
    return ensure_property(site)


def ensure_property(site: AnalyticsSite) -> AnalyticsSite:
    """Attach a site to its zero-config logical property.

    The shortest trusted suffix is the property's domain. For
    ``cmdop.com`` + ``my.cmdop.com`` this yields one ``cmdop.com`` property;
    domains that have no trusted parent remain a one-site property. No public
    suffix heuristic is needed: ``security_domains`` is the explicit ownership
    boundary and therefore the only grouping authority.
    """
    domain = _property_domain(site.domain)
    try:
        property_, _ = AnalyticsProperty.objects.get_or_create(
            domain=domain,
            defaults={"name": domain, "timezone": site.timezone or _default_timezone()},
        )
        if site.property_id != property_.pk:
            AnalyticsSite.objects.filter(pk=site.pk).update(property=property_)
            site.property = property_
    except DatabaseError:
        # During a rolling deploy the code can briefly precede migration 0003.
        # Ingest must continue to work; the next request after migration lazily
        # attaches the site to its property.
        logger.debug("Analytics: properties schema is not ready yet")
        return site
    return site


def _property_domain(domain: str) -> str:
    candidates = [
        trusted for trusted in _trusted_domains()
        if domain == trusted or domain.endswith(f".{trusted}")
    ]
    # The broadest owned suffix is the logical product boundary. Prefer length
    # rather than label count so an unusual but valid host name behaves too.
    return min(candidates, key=len) if candidates else domain


__all__ = ["resolve_site", "claimed_domain", "ensure_property"]
