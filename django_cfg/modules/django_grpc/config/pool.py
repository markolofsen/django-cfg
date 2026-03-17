"""django_grpc.config.pool — Unified gRPC connection pool configuration."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class GrpcPoolConfig(BaseModel):
    """Unified connection pool configuration (single source of truth).

    Replaces the three separate PoolConfig definitions that previously existed in:
    - config/resilience.py  (Pydantic, missing max_age/cleanup_interval/health_check_interval)
    - resilience/config.py  (Pydantic, missing health_check_interval)
    - services/client/pool.py  (dataclass — the only one that actually ran)
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    enabled: bool = Field(default=True, description="Enable connection pooling")
    max_size: int = Field(default=20, ge=1, le=200, description="Maximum channels in pool")
    idle_timeout: float = Field(default=120.0, ge=10.0, le=3600.0, description="Seconds before idle channel is closed")
    min_idle: int = Field(default=2, ge=0, le=20, description="Minimum idle channels to maintain per address")
    max_age: float = Field(default=3600.0, ge=60.0, le=86400.0, description="Maximum channel lifetime in seconds")
    cleanup_interval: float = Field(default=60.0, ge=10.0, le=600.0, description="Seconds between pool cleanup cycles")
    health_check_interval: float = Field(default=30.0, ge=5.0, le=600.0, description="Seconds between idle channel health checks")
    channel_ready_timeout: float = Field(default=5.0, ge=1.0, le=60.0, description="Seconds to wait for channel to become ready")


__all__ = ["GrpcPoolConfig"]
