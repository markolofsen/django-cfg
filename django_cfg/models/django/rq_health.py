"""
RQ Queue-Health Monitor Configuration for django-cfg.

Type-safe configuration for the RQ queue-health monitor — a periodic check
that collects per-queue metrics (depth, oldest job age, failed count, worker
liveness, scheduler lag, orphan-id ratio), evaluates them against thresholds,
and raises Telegram alerts when a queue degrades.

The monitor runs as a periodic RQ scheduled task auto-registered by
``DjangoRQConfig.get_all_schedules()`` and is also exposed as the
``rq_health_check`` management command.

Example:
    ```python
    from django_cfg.models.django.django_rq import DjangoRQConfig
    from django_cfg.models.django.rq_health import RQHealthConfig, QueueHealthThresholds

    django_rq_config = DjangoRQConfig(
        redis_db=1,
        health=RQHealthConfig(
            enabled=True,
            check_interval_sec=60,
            alert_chat_id="-1001234567890",
            monitored_queues=["default", "crm", "high"],
            thresholds=QueueHealthThresholds(depth_critical=2000),
            queue_overrides={
                "crm": QueueHealthThresholds(oldest_job_age_critical_sec=300),
            },
        ),
    )
    ```
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class QueueHealthThresholds(BaseModel):
    """
    Per-metric thresholds for a single queue's health evaluation.

    Each metric has a ``warning`` and (where it makes sense) a ``critical``
    threshold. The overall queue status is the maximum severity across all
    per-metric statuses.

    A queue that is simply deep but actively draining (small oldest-job age,
    workers alive) stays healthy — only depth combined with stale jobs or no
    workers escalates to critical.
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    # Queue depth (number of queued jobs)
    depth_warning: int = Field(
        default=100,
        ge=1,
        description="Queue depth (queued jobs) at or above which status is 'warning'",
    )
    depth_critical: int = Field(
        default=1000,
        ge=1,
        description="Queue depth (queued jobs) at or above which status is 'critical'",
    )

    # Oldest queued job age
    oldest_job_age_warning_sec: int = Field(
        default=600,
        ge=1,
        description="Oldest queued job age in seconds at or above which status is 'warning'",
    )
    oldest_job_age_critical_sec: int = Field(
        default=1800,
        ge=1,
        description="Oldest queued job age in seconds at or above which status is 'critical'",
    )

    # Failed job count
    failed_count_warning: int = Field(
        default=25,
        ge=1,
        description="Failed job count at or above which status is 'warning'",
    )
    failed_count_critical: int = Field(
        default=100,
        ge=1,
        description="Failed job count at or above which status is 'critical'",
    )

    # Worker liveness
    worker_heartbeat_warning_sec: int = Field(
        default=90,
        ge=1,
        description=(
            "Worker heartbeat age in seconds at or above which status is 'warning'. "
            "A queue with no workers AND queued jobs is always 'critical'."
        ),
    )

    # Orphan-id ratio (sampled queued IDs whose rq:job:<id> hash is missing)
    orphan_ratio_warning: float = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="Orphan-id ratio at or above which status is 'warning'",
    )
    orphan_ratio_critical: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Orphan-id ratio at or above which status is 'critical'",
    )

    # Scheduler lag (most-overdue scheduled job)
    scheduler_lag_warning_sec: int = Field(
        default=120,
        ge=1,
        description="Scheduler lag in seconds at or above which status is 'warning'",
    )
    scheduler_lag_critical_sec: int = Field(
        default=600,
        ge=1,
        description="Scheduler lag in seconds at or above which status is 'critical'",
    )


class RQHealthConfig(BaseModel):
    """
    Complete RQ queue-health monitor configuration.

    When ``enabled`` is True, ``DjangoRQConfig.get_all_schedules()`` registers a
    periodic ``run_queue_health_check`` job on ``monitor_queue`` every
    ``check_interval_sec`` seconds.

    Alerting reuses the project's Telegram configuration (see ``TelegramConfig``);
    set ``alert_chat_id`` to route health alerts to a dedicated chat instead of
    the project default.
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    enabled: bool = Field(
        default=True,
        description="Enable the RQ queue-health monitor (auto-registers a periodic check)",
    )

    check_interval_sec: int = Field(
        default=60,
        ge=30,
        description="Interval in seconds between health checks (minimum 30s)",
    )

    monitor_queue: str = Field(
        default="default",
        description="Queue the periodic health-check job itself runs on",
    )

    # Telegram alerting
    telegram_alerts_enabled: bool = Field(
        default=True,
        description="Send Telegram alerts when a queue degrades (requires TelegramConfig)",
    )

    alert_chat_id: Optional[str] = Field(
        default=None,
        description=(
            "Optional Telegram chat ID override for health alerts. "
            "If None, the project's default Telegram chat_id is used."
        ),
    )

    alert_cooldown_sec: int = Field(
        default=1800,
        ge=60,
        description=(
            "Per-(queue, severity) cooldown in seconds between repeated alerts. "
            "A 'critical' alert still fires inside a 'warning' cooldown (escalation)."
        ),
    )

    min_consecutive_breaches: int = Field(
        default=1,
        ge=1,
        description=(
            "Hysteresis: require N consecutive cycles in the same severity "
            "before sending a Telegram alert. 1 = current behaviour (alert on "
            "the first breach). Raise to 3 to filter transient post-restart "
            "noise — a one-cycle blip never alerts, a sustained breach still "
            "does. The streak counter clears on the next healthy cycle and "
            "has a 1h TTL so a stalled monitor never gets stuck near the "
            "threshold."
        ),
    )

    send_recovery_alerts: bool = Field(
        default=True,
        description="Send a recovery (success) message when a previously-alerting queue returns to healthy",
    )

    monitored_queues: Optional[List[str]] = Field(
        default=None,
        description="Queue names to monitor. None means all queues configured in DjangoRQConfig.queues.",
    )

    orphan_sample_size: int = Field(
        default=200,
        ge=10,
        description="Number of queued job IDs to sample when estimating the orphan-id ratio",
    )

    auto_prune_orphan_ids: bool = Field(
        default=False,
        description=(
            "Opt-in: when True, the monitor LREMs orphaned IDs from rq:queue:<q> "
            "after detecting them. When False (default) the monitor only reports."
        ),
    )

    thresholds: QueueHealthThresholds = Field(
        default_factory=QueueHealthThresholds,
        description="Default per-metric thresholds applied to every monitored queue",
    )

    queue_overrides: Dict[str, QueueHealthThresholds] = Field(
        default_factory=dict,
        description="Per-queue threshold overrides keyed by queue name",
    )

    def thresholds_for(self, queue_name: str) -> QueueHealthThresholds:
        """Return the thresholds for a queue (override if present, else defaults)."""
        return self.queue_overrides.get(queue_name, self.thresholds)


__all__ = [
    "QueueHealthThresholds",
    "RQHealthConfig",
]
