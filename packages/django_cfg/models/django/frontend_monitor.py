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


__all__ = ["FrontendMonitorConfig"]
