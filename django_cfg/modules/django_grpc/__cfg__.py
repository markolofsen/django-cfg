"""
django_grpc module configuration.

Controls gRPC server, auth, D1 persistence, and async log worker settings.
Add to your DjangoConfig to enable:

    from django_cfg.modules.django_grpc import DjangoGrpcModuleConfig
    # (loaded automatically — no extra INSTALLED_APPS entry needed)

Example::

    grpc_module = DjangoGrpcModuleConfig(
        enabled=True,
        public_url="grpc.example.com:443",
        server=GrpcServerConfig(host="0.0.0.0", port=50051),
        auth=GrpcAuthConfig(require_auth=True),
    )
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from django_cfg.models.django.django_rq import RQScheduleConfig
from django_cfg.modules.django_grpc.config.auth import GrpcAuthConfig
from django_cfg.modules.django_grpc.config.metrics import MetricsConfig
from django_cfg.modules.django_grpc.config.observability import ObservabilityConfig
from django_cfg.modules.django_grpc.config.persistence import GrpcPersistenceConfig
from django_cfg.modules.django_grpc.config.pool import GrpcPoolConfig
from django_cfg.modules.django_grpc.config.resilience import ResilienceConfig
from django_cfg.modules.django_grpc.config.server import GrpcServerConfig


class DjangoGrpcModuleConfig(BaseModel):
    """Top-level configuration for modules/django_grpc."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    enabled: bool = True

    # ── Server ────────────────────────────────────────────────────────────────
    server: GrpcServerConfig = Field(default_factory=GrpcServerConfig)

    # ── Public / internal URLs (not part of server bind config) ───────────────
    public_url: str | None = Field(default=None, description="Public gRPC URL for external clients")
    internal_url: str | None = Field(default=None, description="Internal container-to-container URL")

    # ── Service registration ───────────────────────────────────────────────────
    handlers_hook: str | list[str] = Field(default="", description="Import path(s) to grpc_handlers function")
    enabled_apps: list[str] = Field(default_factory=list, description="Django apps to expose via gRPC")
    package_prefix: str = Field(default="api", description="Proto package prefix")

    # ── Auth ──────────────────────────────────────────────────────────────────
    auth: GrpcAuthConfig = Field(default_factory=GrpcAuthConfig)

    # ── Sub-configs ───────────────────────────────────────────────────────────
    resilience: ResilienceConfig = Field(default_factory=ResilienceConfig)
    pool: GrpcPoolConfig = Field(default_factory=GrpcPoolConfig)
    persistence: GrpcPersistenceConfig = Field(default_factory=GrpcPersistenceConfig)
    observability: ObservabilityConfig = Field(default_factory=ObservabilityConfig)
    metrics: MetricsConfig = Field(default_factory=MetricsConfig)

    schedules: list[RQScheduleConfig] = [
        RQScheduleConfig(
            func="django_cfg.modules.django_grpc.events.tasks.cleanup_old_grpc_request_logs",
            cron="0 3 * * *",
            description="Cleanup old gRPC request logs",
        ),
        # cleanup_old_grpc_connection_data removed — the 3 connection tables
        # (grpc_connection_states, grpc_connection_events, grpc_connection_metrics)
        # were always empty (write path was dead code) and have been dropped.
    ]


# Module-level settings singleton (defaults)
settings = DjangoGrpcModuleConfig()


__all__ = ["DjangoGrpcModuleConfig", "settings"]
