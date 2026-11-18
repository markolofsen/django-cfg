"""One row per browser error signature.

Key: (``fingerprint``, ``environment``, ``project_name``). A repeat of the same
signature bumps ``count`` and ``last_seen`` and refreshes the latest context; it
never adds a row, so the table is bounded by the number of distinct errors, not
by traffic.
"""

from __future__ import annotations

from django.db import models


class FrontendError(models.Model):
    class EventType(models.TextChoices):
        JS_ERROR = "JS_ERROR", "JS error"
        NETWORK_ERROR = "NETWORK_ERROR", "Network error"
        ERROR = "ERROR", "Error"
        WARNING = "WARNING", "Warning"

    fingerprint = models.CharField(max_length=64, db_index=True)
    environment = models.CharField(max_length=20, blank=True, db_index=True)
    project_name = models.CharField(max_length=100, blank=True, db_index=True)

    event_type = models.CharField(max_length=32, choices=EventType.choices, db_index=True)
    level = models.CharField(max_length=16, default="error", db_index=True)

    count = models.PositiveIntegerField(default=1)
    first_seen = models.DateTimeField(db_index=True)
    last_seen = models.DateTimeField(db_index=True)

    message = models.TextField(blank=True)
    stack_trace = models.TextField(blank=True)
    url = models.TextField(blank=True, help_text="Page URL of the latest occurrence")
    http_status = models.IntegerField(null=True, blank=True)
    http_method = models.CharField(max_length=10, blank=True)
    http_url = models.TextField(blank=True)

    browser = models.CharField(max_length=100, blank=True)
    os = models.CharField(max_length=100, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    session_id = models.CharField(max_length=64, blank=True, help_text="Session of the latest occurrence")
    build_id = models.CharField(max_length=100, blank=True)
    extra = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Frontend error"
        verbose_name_plural = "Frontend errors"
        ordering = ["-last_seen"]
        constraints = [
            models.UniqueConstraint(
                fields=["fingerprint", "environment", "project_name"], name="cfg_fe_signature_uniq"
            ),
        ]

    def __str__(self) -> str:
        return f"[{self.event_type}] {self.message[:80]} (x{self.count})"
