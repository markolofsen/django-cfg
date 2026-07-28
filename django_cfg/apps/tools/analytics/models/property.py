"""A logical analytics property that groups related trusted hosts."""

from __future__ import annotations

from django.db import models


class AnalyticsProperty(models.Model):
    """One first-party property, normally the trusted apex domain.

    A property deliberately aggregates hosts, not browser identities. Browser
    visitor and session ids remain host-scoped; only authenticated users can be
    de-duplicated safely across its member sites.
    """

    domain = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=128, blank=True)
    timezone = models.CharField(max_length=64, default="UTC")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "cfg_analytics"
        db_table = "cfg_analytics_property"
        verbose_name = "Analytics property"
        verbose_name_plural = "Analytics properties"
        ordering = ["domain"]

    def __str__(self) -> str:
        return self.name or self.domain
