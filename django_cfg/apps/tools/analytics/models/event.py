"""AnalyticsEvent — the append-only fact table.

Three decisions here are load-bearing. Changing any of them silently corrupts
data rather than raising, so each is spelled out.

1. ``session_id`` is WRITTEN AT INSERT, never derived.
   It is a deterministic hash (see ``services/identity.py``), so it is known
   *before* the row exists. The tempting alternative — reconstructing sessions
   with a ``LAG()`` window function at read time — leaves this column NULL on
   every row, and every per-user journey query silently returns NULLs.

2. ``user_id`` is written at ingest.
   PostHog's single largest subsystem (``person_distinct_id_overrides`` plus
   partition "squashing") exists purely to retrofit identity onto events that
   were already written anonymously. We know the user at write time. Writing it
   deletes that entire problem before it is created.

3. ``PRIMARY KEY (id, ts)`` — the partition key is in the PK from day one even
   though we do NOT partition yet. Postgres requires the partition key in every
   PK/UNIQUE constraint, so retrofitting it later means a full table rewrite.
   This costs nothing now and keeps the door open.

Indexes follow Umami's uniform ``(site, ts, <dim>)`` prefix: every dashboard
query is scoped to one site plus a time range, so the prefix always applies and
the trailing dimension makes the GROUP BY index-only.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models


class EventName(models.TextChoices):
    PAGEVIEW = "pageview", "Pageview"
    CUSTOM = "custom", "Custom"


class Channel(models.TextChoices):
    """Resolved at INGEST, never at query time.

    Umami re-runs a 12-branch CASE of ILIKE '%...%' over domain lists on every
    dashboard load — unindexable, and the reason they need 14 composite indexes.
    We classify once, on write, and store the answer.
    """

    DIRECT = "direct", "Direct"
    ORGANIC_SEARCH = "organic_search", "Organic Search"
    ORGANIC_SOCIAL = "organic_social", "Organic Social"
    ORGANIC_VIDEO = "organic_video", "Organic Video"
    # Ordered BEFORE organic_search in the classifier: an LLM referrer that
    # falls through to "search" is the most common misclassification today
    # (PostHog currently files perplexity.ai as Organic Search).
    AI = "ai", "AI Assistant"
    REFERRAL = "referral", "Referral"
    PAID_SEARCH = "paid_search", "Paid Search"
    PAID_SOCIAL = "paid_social", "Paid Social"
    EMAIL = "email", "Email"
    AFFILIATE = "affiliate", "Affiliate"
    UNKNOWN = "unknown", "Unknown"


class AnalyticsEvent(models.Model):
    id = models.BigAutoField(primary_key=True)

    site = models.ForeignKey(
        "cfg_analytics.AnalyticsSite",
        on_delete=models.CASCADE,
        related_name="events",
    )

    # ALWAYS UTC. Folded into site-local days at read time. Never store local
    # time: an hourly rollup of local time cannot represent +05:30/+05:45 zones.
    ts = models.DateTimeField(db_index=False)

    # Cookieless. Deterministic hash of (site, ip, ua, daily-rotating salt).
    # The raw IP and UA never reach this table.
    visitor_id = models.UUIDField()

    # Derived from visitor_id + the session window. See the module docstring.
    # related_name is "hits", not "events": AnalyticsSession.events is already a
    # denormalized COUNT, and the reverse accessor would collide with it.
    session = models.ForeignKey(
        "cfg_analytics.AnalyticsSession",
        on_delete=models.CASCADE,
        related_name="hits",
    )

    # The differentiator. NULL for anonymous traffic.
    # AUTH_USER_MODEL, never "auth.User" — django-cfg swaps the user model.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        db_constraint=False,  # keeps a user purge from cascading into 50M rows
    )

    event_name = models.CharField(
        max_length=64,
        choices=EventName.choices,
        default=EventName.PAGEVIEW,
    )

    # Raw URL path, e.g. /en/blog/hello-world
    pathname = models.CharField(max_length=1024)
    # Templated route, e.g. /[locale]/blog/[slug]. Without this, /en/pricing and
    # /ru/pricing fragment into separate "pages" and the top-pages report is junk.
    route = models.CharField(max_length=1024, blank=True)
    # Lifted out of the path into its own dimension for the same reason.
    locale = models.CharField(max_length=16, blank=True)

    hostname = models.CharField(max_length=255, blank=True)
    page_title = models.CharField(max_length=512, blank=True)

    referrer_domain = models.CharField(max_length=255, blank=True)
    channel = models.CharField(
        max_length=32,
        choices=Channel.choices,
        default=Channel.DIRECT,
    )

    utm_source = models.CharField(max_length=255, blank=True)
    utm_medium = models.CharField(max_length=255, blank=True)
    utm_campaign = models.CharField(max_length=255, blank=True)
    utm_content = models.CharField(max_length=255, blank=True)
    utm_term = models.CharField(max_length=255, blank=True)

    # One column pair, not six (gclid/fbclid/msclkid/ttclid/...). The param name
    # is data, not schema.
    click_id = models.CharField(max_length=255, blank=True)
    click_id_param = models.CharField(max_length=32, blank=True)

    # Custom properties. JSONB, NOT an EAV side table: Umami's event_data EAV
    # exists only so one Prisma schema can also compile to ClickHouse, where
    # jsonb does not exist. We are Postgres-only, so that constraint is not ours.
    props = models.JSONField(default=dict, blank=True)

    class Meta:
        app_label = "cfg_analytics"
        db_table = "cfg_analytics_event"
        verbose_name = "Analytics Event"
        verbose_name_plural = "Analytics Events"
        ordering = ["-ts"]
        indexes = [
            # The uniform prefix. Every report is (one site) x (a time range).
            models.Index(fields=["site", "ts"], name="cfg_an_ev_site_ts"),
            models.Index(fields=["site", "ts", "pathname"], name="cfg_an_ev_path"),
            models.Index(fields=["site", "ts", "referrer_domain"], name="cfg_an_ev_ref"),
            models.Index(fields=["site", "ts", "channel"], name="cfg_an_ev_chan"),
            # Sankey / path analysis: LEAD() partitioned by SESSION, never by
            # visitor — partitioning by visitor stitches yesterday's session onto
            # today's and destroys the exit rate.
            models.Index(fields=["site", "session", "ts"], name="cfg_an_ev_sess"),
            # Per-user journey. Partial: user_id is mostly NULL, so this index
            # stays small even on a huge table.
            models.Index(
                fields=["user", "ts"],
                name="cfg_an_ev_user",
                condition=models.Q(user__isnull=False),
            ),
            # "Online now". btree, deliberately NOT brin: measured 26x slower
            # with brin (1.117ms/137 buffers vs 0.041ms/23) because the lossy
            # recheck discards thousands of rows to return a handful.
            models.Index(fields=["ts"], name="cfg_an_ev_ts"),
        ]

    def __str__(self) -> str:
        return f"{self.event_name} {self.pathname}"
