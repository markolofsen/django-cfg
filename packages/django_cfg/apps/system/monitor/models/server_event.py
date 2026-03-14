"""
Server-side error and performance event model.

Stores deduplicated server errors with occurrence counting.
Each unique (exception_type, module, func_name) combination maps
to exactly one ServerEvent row; subsequent occurrences increment
occurrence_count and update last_seen.
"""

import hashlib

from django.conf import settings
from django.db import models
from django.utils import timezone


class ServerEvent(models.Model):
    """
    A deduplicated record of a server-side failure or performance event.

    Unlike FrontendEvent (append-only per occurrence), ServerEvent uses
    upsert semantics: the fingerprint is unique, and repeated occurrences
    increment occurrence_count rather than inserting new rows.

    Capture mechanisms:
    - SERVER_ERROR:        got_request_exception signal (HTTP 500s)
    - UNHANDLED_EXCEPTION: MonitorHandler (logging.Handler) at ERROR/CRITICAL
    - SLOW_QUERY:          execute_wrapper hook via SlowQueryMiddleware
    - RQ_FAILURE:          global RQ ExceptionHandler registered in ready()
    - OOM_KILL:            MonitoringWorker.work_horse_killed_handler
    - LOG_ERROR:           MonitorHandler catching non-exception log records
    """

    class EventType(models.TextChoices):
        SERVER_ERROR = "SERVER_ERROR", "Server Error"
        UNHANDLED_EXCEPTION = "UNHANDLED_EXCEPTION", "Unhandled Exception"
        SLOW_QUERY = "SLOW_QUERY", "Slow Query"
        RQ_FAILURE = "RQ_FAILURE", "RQ Task Failure"
        OOM_KILL = "OOM_KILL", "OOM / Process Kill"
        LOG_ERROR = "LOG_ERROR", "Log Error"

    class Level(models.TextChoices):
        ERROR = "error", "Error"
        WARNING = "warning", "Warning"
        INFO = "info", "Info"
        DEBUG = "debug", "Debug"

    # ── Identity ──────────────────────────────────────────────────────────────

    fingerprint = models.CharField(
        max_length=16,
        unique=True,
        db_index=True,
        help_text=(
            "sha256(exception_type::module::func_name)[:16]. "
            "Does NOT include line numbers — stable across deploys."
        ),
    )

    # ── Classification ────────────────────────────────────────────────────────

    event_type = models.CharField(
        max_length=25,
        choices=EventType.choices,
        db_index=True,
    )

    level = models.CharField(
        max_length=10,
        choices=Level.choices,
        default=Level.ERROR,
        db_index=True,
    )

    # ── Error payload ─────────────────────────────────────────────────────────

    message = models.TextField(
        help_text="Short error description or exception message",
    )

    stack_trace = models.TextField(
        null=True,
        blank=True,
        help_text="Full formatted traceback (sanitized — no PII)",
    )

    # ── Logger context (for LOG_ERROR events) ─────────────────────────────────

    logger_name = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Python logger name (e.g. 'django.request', 'myapp.tasks')",
    )

    # ── Request context (for SERVER_ERROR events) ─────────────────────────────

    url = models.TextField(
        blank=True,
        default="",
        help_text="Request URL where the error occurred",
    )

    http_method = models.CharField(
        max_length=10,
        blank=True,
        default="",
        help_text="HTTP method (GET, POST, …)",
    )

    http_status = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="HTTP status code returned to the client",
    )

    # ── Source location ───────────────────────────────────────────────────────

    func_name = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Function or method name where the error originated",
    )

    module = models.CharField(
        max_length=300,
        blank=True,
        default="",
        help_text="Python module path (e.g. 'myapp.views.orders')",
    )

    lineno = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=(
            "Line number at time of first occurrence — display only, "
            "NOT part of the fingerprint"
        ),
    )

    # ── Extra / meta ──────────────────────────────────────────────────────────

    extra = models.JSONField(
        default=dict,
        blank=True,
        help_text=(
            "Arbitrary structured context: RQ job_id, queue name, "
            "slow query SQL, OOM process info, etc."
        ),
    )

    project_name = models.CharField(
        max_length=100,
        blank=True,
        default="",
        db_index=True,
        help_text="Django project / service name",
    )

    environment = models.CharField(
        max_length=20,
        blank=True,
        default="",
        db_index=True,
        help_text="production / staging / development",
    )

    # ── Deduplication counters ────────────────────────────────────────────────

    occurrence_count = models.IntegerField(
        default=1,
        help_text="How many times this fingerprint has been seen",
    )

    first_seen = models.DateTimeField(
        auto_now_add=True,
        help_text="When this fingerprint was first recorded",
    )

    last_seen = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text="When this fingerprint was most recently triggered",
    )

    # ── Resolution tracking ───────────────────────────────────────────────────

    is_resolved = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Marked resolved by a team member",
    )

    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="resolved_server_events",
        help_text="User who marked this event as resolved",
    )

    class Meta:
        app_label = "django_cfg_monitor"
        verbose_name = "Server Event"
        verbose_name_plural = "Server Events"
        ordering = ["-last_seen"]
        indexes = [
            # Primary dedup lookup
            models.Index(fields=["fingerprint"], name="cfg_srv_fingerprint_idx"),
            # Triage dashboard: recent unresolved errors
            models.Index(fields=["last_seen", "is_resolved"], name="cfg_srv_last_seen_idx"),
            # Filter by type in admin
            models.Index(fields=["event_type", "last_seen"], name="cfg_srv_type_idx"),
            # Environment + project drill-down
            models.Index(fields=["project_name", "environment", "last_seen"], name="cfg_srv_project_idx"),
        ]

    def __str__(self) -> str:
        status = "RESOLVED" if self.is_resolved else "OPEN"
        return (
            f"[{self.event_type}][{status}] {self.message[:60]} "
            f"(x{self.occurrence_count})"
        )

    # ── Fingerprint helpers ───────────────────────────────────────────────────

    @classmethod
    def compute_fingerprint(
        cls,
        exception_type: str,
        module: str,
        func_name: str,
    ) -> str:
        """
        Compute a stable 16-character fingerprint.

        Algorithm: sha256("{exception_type}::{module}::{func_name}")[:16]

        Line numbers are explicitly excluded so that the same logical error
        at the same code location deduplicates across deploys even when
        surrounding lines are added or removed.
        """
        raw = f"{exception_type}::{module}::{func_name}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    @classmethod
    def record(
        cls,
        *,
        exception_type: str,
        module: str,
        func_name: str,
        event_type: str,
        message: str,
        db_alias: str = "default",
        **kwargs,
    ) -> "ServerEvent":
        """
        Upsert helper: create a new ServerEvent or increment occurrence_count.

        Uses db_alias (default "monitor") to avoid ATOMIC_REQUESTS rollback.

        On regression (error reappears after being resolved), clears is_resolved.
        """
        fingerprint = cls.compute_fingerprint(exception_type, module, func_name)
        now = timezone.now()

        obj, created = cls.objects.using(db_alias).get_or_create(
            fingerprint=fingerprint,
            defaults={
                "event_type": event_type,
                "message": message,
                "module": module,
                "func_name": func_name,
                "last_seen": now,
                **kwargs,
            },
        )
        if not created:
            cls.objects.using(db_alias).filter(pk=obj.pk).update(
                occurrence_count=models.F("occurrence_count") + 1,
                last_seen=now,
                # Reopen if previously resolved (regression detection)
                is_resolved=False,
                resolved_at=None,
                resolved_by=None,
            )
            obj.refresh_from_db()
        return obj
