"""AnalyticsSite — the tenant boundary and the timezone anchor.

``timezone`` is the reason this model exists. Buckets are stored in UTC and
folded into *site-local* days at read time (see ``services/reports.py``), which
is what makes a timezone change a zero-cost config edit rather than a rollup
rebuild.
"""

from __future__ import annotations

from django.db import models


class AnalyticsSite(models.Model):
    domain = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=128, blank=True)

    # IANA name, e.g. "Europe/Berlin". Never a fixed UTC offset — that would
    # break DST. Reports fold UTC buckets into local days with this at read time.
    timezone = models.CharField(max_length=64, default="UTC")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "cfg_analytics"
        db_table = "cfg_analytics_site"
        verbose_name = "Analytics Site"
        verbose_name_plural = "Analytics Sites"
        ordering = ["domain"]

    def __str__(self) -> str:
        return self.name or self.domain
