"""
Analytics configuration model.

First-party, self-hosted analytics: pageviews, sessions, user journeys.

Design constraint (non-negotiable): **zero extra runtime processes.** No Celery,
no RQ worker, no consumer daemon, no sidecar. Ingest is a synchronous INSERT in
the request thread — the same baseline Umami and Shynet ship in production.
See ``@dev/active/analytics/PLAN.md``.
"""

from pydantic import BaseModel, Field


class AnalyticsConfig(BaseModel):
    """
    Analytics app configuration.

    Example:
        ```python
        from django_cfg import DjangoConfig, AnalyticsConfig

        class MyConfig(DjangoConfig):
            analytics = AnalyticsConfig()
        ```
    """

    enabled: bool = Field(
        default=True,
        description="Enable analytics app (auto-adds to INSTALLED_APPS)",
    )

    # ── Ingest ────────────────────────────────────────────────────────────────

    ingest_path: str = Field(
        default="collect",
        description=(
            "Path segment of the ingest endpoint, mounted under /cfg/analytics/. "
            "Configurable on purpose: EasyPrivacy and friends block ad-blocker "
            "rules by PATH, not domain — a fixed path shipped in an open-source "
            "package gets filter-listed once, for everyone. Change it to dodge."
        ),
    )

    max_batch_size: int = Field(
        default=25,
        ge=1,
        le=200,
        description=(
            "Max events accepted per POST. The browser's keepalive quota is 64KB "
            "per document and is SHARED between sendBeacon and fetch(keepalive), "
            "so oversized batches are silently dropped client-side."
        ),
    )

    fast_commit: bool = Field(
        default=True,
        description=(
            "Run the ingest INSERT under `SET LOCAL synchronous_commit = off`. "
            "Measured ~19x faster on real durable storage (1.895ms -> 0.098ms); "
            "the trade is losing the last ~200ms of events on a hard crash, which "
            "for analytics is fine. Unlike UNLOGGED tables this is per-transaction, "
            "crash-safe for the rest of the DB, and replication-safe."
        ),
    )

    # ── Sessions ──────────────────────────────────────────────────────────────

    session_timeout_minutes: int = Field(
        default=30,
        ge=1,
        description="Idle gap that ends a session (industry standard: 30 min).",
    )

    salt_rotation_days: int = Field(
        default=1,
        ge=1,
        description=(
            "How often the visitor-id salt rotates. Default 1 day. "
            "(Umami defaults to a MONTH — too weak a pseudonym. The previous "
            "period's salt is kept live so rotation does not sever in-flight "
            "sessions.)"
        ),
    )

    # ── Privacy ───────────────────────────────────────────────────────────────

    respect_dnt: bool = Field(
        default=False,
        description=(
            "Drop events when the browser sends DNT: 1. Off by default because "
            "DNT is deprecated and unreliable (Safari removed it entirely)."
        ),
    )

    store_user_id: bool = Field(
        default=True,
        description=(
            "Attribute events to the authenticated user. This is the whole point "
            "of first-party analytics — Plausible/Umami structurally cannot do it. "
            "Turn off for a strictly anonymous deployment."
        ),
    )


__all__ = ["AnalyticsConfig"]
