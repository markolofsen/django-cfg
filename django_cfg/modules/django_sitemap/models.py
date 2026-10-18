"""IndexNow state: what each host last submitted, and every POST.

The diff state is what makes a run safe to repeat. Only an accepted batch is
written to it, so a refused or failed run is retried by the next one, and a
URL that leaves the sitemap is sent once, as removed.
"""
from __future__ import annotations

import hashlib

from django.db import models


def url_digest(url: str) -> str:
    """SHA-1 of the URL: the unique key, so a long URL cannot outgrow an index."""
    return hashlib.sha1(url.encode("utf-8")).hexdigest()


class IndexNowHost(models.Model):
    """One public host, with its run state."""

    host = models.CharField(max_length=255, unique=True)
    # Null until the first run has recorded the URLs without sending them.
    seeded_at = models.DateTimeField(null=True, blank=True)
    last_run_at = models.DateTimeField(null=True, blank=True)
    # Start of the last run that sent everything it found; `extra_urls` reads from here.
    last_success_at = models.DateTimeField(null=True, blank=True)
    last_status = models.CharField(max_length=120, blank=True)

    class Meta:
        app_label = "django_sitemap"
        ordering = ("host",)
        verbose_name = "IndexNow host"

    def __str__(self) -> str:
        return self.host


class IndexNowUrl(models.Model):
    """One URL as last submitted (or seeded). This is the diff state."""

    host = models.ForeignKey(IndexNowHost, on_delete=models.CASCADE, related_name="urls")
    url = models.TextField()
    digest = models.CharField(max_length=40)
    # Empty for a source without a lastmod value on this row: sent only when it appears or goes.
    lastmod = models.CharField(max_length=40, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "django_sitemap"
        verbose_name = "IndexNow URL"
        constraints = [
            models.UniqueConstraint(fields=("host", "digest"), name="django_sitemap_indexnow_url_unique"),
        ]


class IndexNowSubmission(models.Model):
    """Append-only log of one POST to the IndexNow endpoint."""

    host = models.CharField(max_length=255, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    url_count = models.PositiveIntegerField()
    # Null when the request never got an answer (timeout, DNS).
    http_status = models.PositiveSmallIntegerField(null=True, blank=True)
    response_excerpt = models.CharField(max_length=500, blank=True)
    sample_urls = models.JSONField(default=list, blank=True)

    class Meta:
        app_label = "django_sitemap"
        ordering = ("-created_at",)
        verbose_name = "IndexNow submission"

    @property
    def accepted(self) -> bool:
        return self.http_status in (200, 202)
