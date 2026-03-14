"""
Frontend event model — stores every error, log, or metric sent by the browser.
"""

from django.conf import settings
from django.db import models

from .session import AnonymousSession


class FrontendEvent(models.Model):
    """
    A single event captured from the browser: JS error, network failure,
    console log, page view, or performance metric.
    """

    class EventType(models.TextChoices):
        ERROR = "ERROR", "Error"
        WARNING = "WARNING", "Warning"
        INFO = "INFO", "Info"
        PAGE_VIEW = "PAGE_VIEW", "Page View"
        PERFORMANCE = "PERFORMANCE", "Performance"
        NETWORK_ERROR = "NETWORK_ERROR", "Network Error"
        JS_ERROR = "JS_ERROR", "JS Error"
        CONSOLE = "CONSOLE", "Console"

    class Level(models.TextChoices):
        ERROR = "error", "Error"
        WARN = "warn", "Warning"
        INFO = "info", "Info"
        DEBUG = "debug", "Debug"

    # ── Core ──────────────────────────────────────────────────────────────────

    event_type = models.CharField(
        max_length=20,
        choices=EventType.choices,
        db_index=True,
    )

    level = models.CharField(
        max_length=10,
        choices=Level.choices,
        default=Level.INFO,
        db_index=True,
    )

    message = models.TextField()

    stack_trace = models.TextField(
        blank=True,
        default="",
        help_text="Full stack trace for JS errors",
    )

    # ── Page context ──────────────────────────────────────────────────────────

    url = models.TextField(
        blank=True,
        default="",
        help_text="Page URL where the event occurred",
    )

    # ── Network context (for NETWORK_ERROR) ───────────────────────────────────

    http_status = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="HTTP status code of the failed request",
    )

    http_method = models.CharField(
        max_length=10,
        blank=True,
        default="",
        help_text="HTTP method of the failed request",
    )

    http_url = models.TextField(
        blank=True,
        default="",
        help_text="URL of the failed API call",
    )

    # ── Client info ───────────────────────────────────────────────────────────

    user_agent = models.TextField(blank=True, default="")

    ip_address = models.GenericIPAddressField()

    device_type = models.CharField(
        max_length=10,
        blank=True,
        default="",
        help_text="mobile / tablet / desktop",
    )

    os = models.CharField(max_length=50, blank=True, default="")

    browser = models.CharField(max_length=50, blank=True, default="")

    # ── Deduplication ─────────────────────────────────────────────────────────

    fingerprint = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text="Client-generated hash for deduplication (e.g. sha256 of message+stack+url)",
    )

    # ── Relations ─────────────────────────────────────────────────────────────

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="frontend_events",
        help_text="Authenticated user (null for anonymous visitors)",
    )

    anonymous_session = models.ForeignKey(
        AnonymousSession,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="events",
    )

    # ── Extra / meta ──────────────────────────────────────────────────────────

    extra = models.JSONField(
        default=dict,
        blank=True,
        help_text="Arbitrary extra data from the client",
    )

    build_id = models.CharField(
        max_length=100,
        blank=True,
        default="",
        db_index=True,
        help_text="Next.js BUILD_ID — links event to the exact deploy for source map deminification",
    )

    project_name = models.CharField(
        max_length=100,
        blank=True,
        default="",
        db_index=True,
        help_text="Frontend project name (useful when multiple frontends share one backend)",
    )

    environment = models.CharField(
        max_length=20,
        blank=True,
        default="",
        db_index=True,
        help_text="production / staging / development",
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        app_label = "django_cfg_monitor"
        verbose_name = "Frontend Event"
        verbose_name_plural = "Frontend Events"
        ordering = ["-created_at"]
        indexes = [
            # Dedup: same fingerprint+url within a time window
            models.Index(fields=["fingerprint", "url", "created_at"]),
            # Spike detection: errors per IP per minute
            models.Index(fields=["ip_address", "event_type", "created_at"]),
            # Per-session hourly cap
            models.Index(fields=["anonymous_session", "created_at"]),
        ]

    def __str__(self) -> str:
        who = self.user or (self.anonymous_session and str(self.anonymous_session.session_id)[:8]) or self.ip_address
        return f"[{self.event_type}] {self.message[:60]} — {who}"
