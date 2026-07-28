"""Cookieless visitor and session identity.

The IP and User-Agent NEVER reach the database. They are inputs to a one-way
hash and are then discarded.

Why a deterministic hash and not a random uuid4 + cache map
-----------------------------------------------------------
GoatCounter's design is strictly more private: it keeps ``ua-ip-site`` in an
in-memory map and stores only a random uuid4, so there is no hash to attack
*because there is no hash*. We do not use it, and the reason is deployment, not
privacy:

    that design's CORRECTNESS depends on a shared cache.

With LocMemCache and N gunicorn workers the map fragments per worker and the
same visitor silently becomes N sessions. django-cfg is a *library* — we do not
control the deployment, and a design that quietly produces garbage for everyone
who did not configure Redis is not acceptable. A stateless function is always
correct. The cache, when present, is used only as an accelerator.

We close the privacy gap by fixing what Umami and Shynet get wrong:
  - Umami salts with sha256(date) — a nonce, not a secret. Recomputable by
    anyone, so effectively unsalted.
  - Shynet ships AGGRESSIVE_HASH_SALTING = False by default, i.e. no secret
    salt at all: anyone who knows a target's IP+UA can recompute their id.

Ours is derived from SECRET_KEY and rotates daily (Umami rotates monthly, which
is a far weaker pseudonym). The previous period's salt is kept live so a
rotation at midnight does not sever in-flight sessions.
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import date, datetime, timedelta

from django.conf import settings

# Stable namespace for uuid5. Arbitrary but must never change, or every existing
# visitor_id would be reassigned.
_NAMESPACE = uuid.UUID("6f9b1e4a-0d3f-4c8a-9f2b-7c5d1a8e3b60")


def _salt_for(day: date, rotation_days: int) -> str:
    """Secret, time-boxed salt.

    Bucketing the ordinal means the salt is stable within a rotation window and
    unguessable outside it (SECRET_KEY is the secret; the date alone is not).
    """
    bucket = day.toordinal() // max(rotation_days, 1)
    return hashlib.sha256(
        f"{settings.SECRET_KEY}:analytics:{bucket}".encode()
    ).hexdigest()


def visitor_id(
    *,
    site_id: int,
    ip: str,
    user_agent: str,
    now: datetime,
    rotation_days: int = 1,
) -> uuid.UUID:
    """Stable per-(visitor, rotation window) id. The IP/UA are not recoverable."""
    salt = _salt_for(now.date(), rotation_days)
    digest = hashlib.sha256(
        f"{site_id}|{ip}|{user_agent}|{salt}".encode()
    ).hexdigest()
    return uuid.uuid5(_NAMESPACE, digest)


def previous_visitor_id(
    *,
    site_id: int,
    ip: str,
    user_agent: str,
    now: datetime,
    rotation_days: int = 1,
) -> uuid.UUID:
    """The id this visitor had in the PREVIOUS salt window.

    Checked as a fallback so a salt rotation does not split an in-flight session
    in two (Plausible does the same: find_session(id) or find_session(prev_id)).
    """
    previous_day = now.date() - timedelta(days=max(rotation_days, 1))
    salt = _salt_for(previous_day, rotation_days)
    digest = hashlib.sha256(
        f"{site_id}|{ip}|{user_agent}|{salt}".encode()
    ).hexdigest()
    return uuid.uuid5(_NAMESPACE, digest)


def session_id(*, visitor: uuid.UUID, window_start: datetime) -> uuid.UUID:
    """Session id for a visitor within a given session window.

    Deterministic, so it is known BEFORE the event row is inserted — which is
    precisely what lets AnalyticsEvent.session_id be written rather than derived.
    """
    return uuid.uuid5(_NAMESPACE, f"{visitor}|{window_start.isoformat()}")


def server_visitor_id(*, site_id: int, user_id: int) -> uuid.UUID:
    """Stable opaque identity for trusted non-browser facts.

    A server fact belongs to an authenticated person, not to an IP/UA-derived
    browser visitor.  This value is deliberately separate from ``visitor_id``:
    it lets the session invariant remain true while ``is_measurement=False``
    keeps the fact out of traffic metrics.
    """
    digest = hashlib.sha256(
        f"{settings.SECRET_KEY}:analytics:server:{site_id}:{user_id}".encode()
    ).hexdigest()
    return uuid.uuid5(_NAMESPACE, digest)


__all__ = ["visitor_id", "previous_visitor_id", "server_visitor_id", "session_id"]
