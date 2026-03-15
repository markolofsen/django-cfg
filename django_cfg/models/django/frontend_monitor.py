"""
Frontend Monitor configuration model.
"""

from pydantic import BaseModel, Field


class FrontendMonitorConfig(BaseModel):
    """
    Frontend error monitoring configuration (Sentry-like browser event collection).

    Example:
        ```python
        from django_cfg import DjangoConfig, FrontendMonitorConfig

        class MyConfig(DjangoConfig):
            frontend_monitor = FrontendMonitorConfig()
        ```
    """

    enabled: bool = Field(default=True, description="Enable frontend monitor app")

    retention_days: int = Field(
        default=90,
        description="Delete events older than N days (0 = keep forever)",
    )

    telegram_alerts_enabled: bool = Field(
        default=True,
        description="Send Telegram alerts for error spikes and unhandled JS errors",
    )

    spike_threshold: int = Field(
        default=5,
        description="Number of errors per minute from same IP to trigger a spike alert",
    )

    max_events_per_session_per_hour: int = Field(
        default=500,
        description="Max events per anonymous session per hour (anti-spam)",
    )

    dedup_window_seconds: int = Field(
        default=60,
        description="Seconds window for deduplicating identical events",
    )

    max_batch_size: int = Field(
        default=50,
        description="Max events per ingest request",
    )

    # ── Server-side capture ───────────────────────────────────────────────────

    server_capture_enabled: bool = Field(
        default=True,
        description=(
            "Capture server-side exceptions (500 errors, logging errors, RQ failures) "
            "into ServerEvent. Requires a 'monitor' database alias in DATABASES."
        ),
    )

    monitor_db_alias: str = Field(
        default="monitor",
        description=(
            "Database alias for ServerEvent writes. Must be a separate alias to "
            "prevent ATOMIC_REQUESTS rollback from losing error records."
        ),
    )

    slow_query_threshold_ms: int = Field(
        default=500,
        description="Capture SQL queries slower than this (ms). Set 0 to disable.",
    )

    server_events_retention_days: int = Field(
        default=90,
        description=(
            "Delete resolved ServerEvent records older than N days (0 = keep forever). "
            "Open (unresolved) events are never auto-deleted."
        ),
    )

    server_capture_ignore_loggers: list[str] = Field(
        default_factory=list,
        description=(
            "Logger names to exclude from MonitorHandler capture. "
            "Tip: add 'django.request' to avoid double-capture with got_request_exception."
        ),
    )


__all__ = ["FrontendMonitorConfig"]
