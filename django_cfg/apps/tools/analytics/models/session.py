"""AnalyticsSession — one row per visit. All mutable state lives here.

The event table is append-only; everything that gets *updated* (pageview count,
duration, exit page, bounce flag) is on this row. That keeps the hot write path
a pure INSERT.

``session_id`` is a deterministic hash, not a random uuid4 — see
``services/identity.py`` for why (short version: a random id requires a shared
cache to be *correct*, and django-cfg is a library that does not control the
deployment; a stateless function is always correct).

The dimensions here are denormalized on purpose: browser/os/country cannot change
within a single visit, so storing them per-event would be pure waste.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models


class DeviceType(models.TextChoices):
    DESKTOP = "desktop", "Desktop"
    MOBILE = "mobile", "Mobile"
    TABLET = "tablet", "Tablet"
    BOT = "bot", "Bot"
    UNKNOWN = "unknown", "Unknown"


class AnalyticsSession(models.Model):
    # Deterministic: uuid5(namespace, f"{site}{ip}{ua}{salt}{window}").
    # Known before the first INSERT, which is what lets events carry it.
    id = models.UUIDField(primary_key=True, editable=False)

    site = models.ForeignKey(
        "cfg_analytics.AnalyticsSite",
        on_delete=models.CASCADE,
        related_name="sessions",
    )

    visitor_id = models.UUIDField()

    # AUTH_USER_MODEL, never "auth.User" — django-cfg swaps the user model.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        db_constraint=False,
    )

    started_at = models.DateTimeField()
    last_seen_at = models.DateTimeField()

    entry_pathname = models.CharField(max_length=1024, blank=True)
    exit_pathname = models.CharField(max_length=1024, blank=True)

    pageviews = models.PositiveIntegerField(default=0)
    events = models.PositiveIntegerField(default=0)
    duration_sec = models.PositiveIntegerField(default=0)

    # A visit with a single pageview. Derived from `pageviews`, materialized so
    # the bounce-rate report is an index-only aggregate instead of a subquery.
    is_bounce = models.BooleanField(default=True)

    # ── Acquisition (fixed for the life of the visit) ─────────────────────────
    channel = models.CharField(max_length=32, blank=True)
    referrer_domain = models.CharField(max_length=255, blank=True)
    utm_source = models.CharField(max_length=255, blank=True)
    utm_medium = models.CharField(max_length=255, blank=True)
    utm_campaign = models.CharField(max_length=255, blank=True)

    # ── Client (parsed at ingest; the raw UA string is never stored) ──────────
    browser = models.CharField(max_length=32, blank=True)
    os = models.CharField(max_length=32, blank=True)
    device = models.CharField(
        max_length=16,
        choices=DeviceType.choices,
        default=DeviceType.UNKNOWN,
    )
    language = models.CharField(max_length=35, blank=True)

    # ISO-3166 alpha-2. Resolved from IP, which is then discarded.
    country = models.CharField(max_length=2, blank=True)

    class Meta:
        app_label = "cfg_analytics"
        db_table = "cfg_analytics_session"
        verbose_name = "Analytics Session"
        verbose_name_plural = "Analytics Sessions"
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["site", "started_at"], name="cfg_an_sess_site_start"),
            models.Index(fields=["site", "visitor_id"], name="cfg_an_sess_visitor"),
            models.Index(
                fields=["user", "started_at"],
                name="cfg_an_sess_user",
                condition=models.Q(user__isnull=False),
            ),
        ]

    def __str__(self) -> str:
        return f"{self.visitor_id} @ {self.started_at:%Y-%m-%d %H:%M}"
