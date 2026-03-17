"""django_grpc.config.persistence — D1 retention and async log worker configuration."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class LogWorkerConfig(BaseModel):
    """Async D1 log worker buffering configuration.

    Previously these values lived as bare module-level constants in
    events/log_worker.py and were NOT read from DjangoGrpcModuleConfig,
    making the log_worker_* fields on the top-level config silently inert.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    batch_size: int = Field(default=50, ge=10, le=500, description="Rows flushed per D1 batch call")
    flush_interval: float = Field(default=5.0, ge=1.0, le=60.0, description="Max seconds between flushes")
    queue_size: int = Field(default=2000, ge=100, le=50_000, description="In-memory queue cap (drops on overflow)")


class GrpcPersistenceConfig(BaseModel):
    """D1 persistence settings: retention TTLs, CAS retry config, and log worker."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    log_requests: bool = Field(default=True, description="Write request logs to D1")
    retention_request_days: int = Field(default=90, ge=1, le=365, description="Request log TTL in days")
    optimistic_lock_retries: int = Field(default=3, ge=1, le=10, description="CAS retry attempts for connection state updates")
    jitter_cap_ms: float = Field(
        default=500.0,
        ge=10.0,
        le=5000.0,
        description="Cap for CAS retry exponential jitter in milliseconds",
    )
    log_worker: LogWorkerConfig = Field(default_factory=LogWorkerConfig)


__all__ = ["LogWorkerConfig", "GrpcPersistenceConfig"]
