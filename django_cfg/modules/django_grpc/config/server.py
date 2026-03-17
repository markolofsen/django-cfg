"""django_grpc.config.server — gRPC server configuration."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from django_cfg.modules.django_grpc.config.tls import TLSConfig


class GrpcKeepaliveConfig(BaseModel):
    """TCP keepalive / HTTP2 ping configuration for the gRPC server."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    # G-5 fix: time_ms/timeout_ms bumped to recommended production values.
    # Old defaults (10_000 / 5_000) were too aggressive; gRPC recommends
    # 30 000 ms interval and 10 000 ms timeout to avoid spurious disconnects
    # under network blips.
    time_ms: int = Field(
        default=30_000,
        ge=1_000,
        description="Keepalive ping interval (ms). Default 30 000 (was 10 000).",
    )
    timeout_ms: int = Field(
        default=10_000,
        ge=1_000,
        description="Keepalive ping timeout (ms). Default 10 000 (was 5 000).",
    )
    permit_without_calls: bool = Field(default=True, description="Allow pings even with no active calls")
    max_pings_without_data: int = Field(default=0, ge=0, description="0 = unlimited")
    http2_min_ping_interval_ms: int = Field(default=5_000, ge=1_000, description="Minimum time between HTTP/2 pings (ms)")

    # G-5 fix: three production-critical keepalive options that were missing.
    # Without max_connection_idle_ms, idle connections stay open indefinitely
    # accumulating C-core state. Without max_connection_age_ms, long-lived
    # connections cause memory fragmentation in the C-core.
    max_connection_idle_ms: int = Field(
        default=600_000,
        ge=0,
        description="Close idle connections after N ms. 0 = disabled. Default 600 000 (10 min).",
    )
    max_connection_age_ms: int = Field(
        default=3_600_000,
        ge=0,
        description="Max connection lifetime (ms); forces reconnect to recycle C-core state. 0 = disabled. Default 3 600 000 (1 h).",
    )
    max_connection_age_grace_ms: int = Field(
        default=60_000,
        ge=0,
        description="Grace period before forced close after max_connection_age_ms. Default 60 000 (1 min).",
    )


class GrpcServerConfig(BaseModel):
    """gRPC server bind and limits configuration."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    host: str = Field(default="[::]", description="IPv4/IPv6 listen address")
    port: int = Field(default=50051, ge=1, le=65535)
    max_workers: int = Field(default=10, ge=1, le=256)
    max_send_message_length: int = Field(default=4 * 1024 * 1024, description="Max outbound message size (bytes)")
    max_receive_message_length: int = Field(default=4 * 1024 * 1024, description="Max inbound message size (bytes)")
    enable_reflection: bool = Field(
        default=False,
        description="grpcurl / server reflection support. Enable only in development; exposes full schema publicly.",
    )
    enable_health_check: bool = Field(default=True, description="Health check endpoint")
    shutdown_grace_seconds: float = Field(default=5.0, ge=0.0, le=60.0, description="Graceful shutdown wait time")
    keepalive: GrpcKeepaliveConfig = Field(default_factory=GrpcKeepaliveConfig)

    # K-3: reflection auth controls.
    # reflection_require_auth=False (default) preserves backward-compatible behaviour:
    # reflection is publicly accessible regardless of require_auth.
    # Set reflection_require_auth=True to gate reflection behind JWT auth.
    # reflection_admin_key allows grpcurl / Postman access in auth-required environments
    # via x-admin-key gRPC metadata — avoids needing a full JWT token for dev tooling.
    reflection_require_auth: bool = Field(
        default=False,
        description=(
            "When True, the reflection endpoint requires JWT auth (removed from "
            "public methods list). When False (default), reflection is publicly "
            "readable regardless of require_auth — backward compatible."
        ),
    )
    reflection_admin_key: Optional[str] = Field(
        default=None,
        description=(
            "If set, requests with x-admin-key metadata matching this value bypass "
            "reflection auth. Allows grpcurl/Postman access in auth-required environments."
        ),
    )

    # I-1: server-side TLS configuration.
    # When None (default), the server binds an insecure port (backward compatible).
    # When set, add_secure_port() is called with ssl_server_credentials() instead of
    # add_insecure_port(). Requires cert_path + key_path in the TLSConfig.
    tls: Optional[TLSConfig] = Field(
        default=None,
        description=(
            "Server TLS configuration. When None (default), the server binds an insecure "
            "port. Set TLSConfig(enabled=True, cert_path=..., key_path=...) to enable TLS."
        ),
    )

    @property
    def address(self) -> str:
        return f"{self.host}:{self.port}"

    def get_channel_options(self) -> list[tuple[str, object]]:
        """Build grpc_options list for grpc.aio.server()."""
        return [
            ("grpc.max_send_message_length", self.max_send_message_length),
            ("grpc.max_receive_message_length", self.max_receive_message_length),
            ("grpc.keepalive_time_ms", self.keepalive.time_ms),
            ("grpc.keepalive_timeout_ms", self.keepalive.timeout_ms),
            ("grpc.keepalive_permit_without_calls", int(self.keepalive.permit_without_calls)),
            ("grpc.http2.min_time_between_pings_ms", self.keepalive.http2_min_ping_interval_ms),
            ("grpc.http2.max_pings_without_data", self.keepalive.max_pings_without_data),
            # G-5: three missing production-critical keepalive options
            ("grpc.max_connection_idle_ms", self.keepalive.max_connection_idle_ms),
            ("grpc.max_connection_age_ms", self.keepalive.max_connection_age_ms),
            ("grpc.max_connection_age_grace_ms", self.keepalive.max_connection_age_grace_ms),
        ]



__all__ = ["GrpcKeepaliveConfig", "GrpcServerConfig"]
