"""
django_rq module configuration.

Controls D1 metrics capture for RQ jobs and workers.
Add to your DjangoConfig to enable:

    from django_cfg.modules.django_rq import DjangoRQModuleConfig
    # (loaded automatically — no extra INSTALLED_APPS entry needed)
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class DjangoRQModuleConfig(BaseModel):
    """Configuration for django_rq D1 metrics module."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    capture_job_events: bool = True       # Capture lifecycle events (queued/started/finished)
    capture_worker_heartbeat: bool = True  # Write worker state snapshots to D1
    retention_days: int = 30              # How long to keep rq_job_events
    max_stack_trace_bytes: int = 10_000   # Truncate stack traces to this size


# Module-level settings singleton
settings = DjangoRQModuleConfig()


__all__ = ["DjangoRQModuleConfig", "settings"]
