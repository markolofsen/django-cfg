"""
django_grpc.config.client — gRPC client channel configuration.

Consolidates all channel options that were previously hardcoded.

Usage:
    from django_cfg.modules.django_grpc.config.client import ClientChannelConfig

    config = ClientChannelConfig(
        address="grpc.example.com:443",
        use_tls=True,
        max_retries=5,
    )

    options = config.get_channel_options()
    channel = grpc.aio.insecure_channel(config.address, options=options)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .constants import (
    GRPC_CONNECT_TIMEOUT,
    GRPC_DEFAULT_HOST,
    GRPC_DEFAULT_PORT,
    GRPC_ENABLE_RETRIES,
    GRPC_KEEPALIVE_PERMIT_WITHOUT_CALLS,
    GRPC_KEEPALIVE_TIME_MS,
    GRPC_KEEPALIVE_TIMEOUT_MS,
    GRPC_MAX_CONNECTION_IDLE_MS,
    GRPC_MAX_MESSAGE_LENGTH,
    GRPC_MAX_PINGS_WITHOUT_DATA,
    GRPC_MAX_RETRIES,
    GRPC_RPC_CALL_TIMEOUT,
)

if TYPE_CHECKING:
    import grpc


class ClientChannelConfig(BaseModel):
    """Configuration for gRPC client channel creation."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    # === Target ===
    address: str = Field(..., description="Server address in 'host:port' format")

    # === Connection Options ===
    wait_for_ready: bool = Field(default=True)
    connect_timeout: float = Field(default=GRPC_CONNECT_TIMEOUT, gt=0.0, le=300.0)
    call_timeout: float = Field(default=GRPC_RPC_CALL_TIMEOUT, gt=0.0, le=600.0)

    # === Keepalive ===
    keepalive_time_ms: int = Field(default=GRPC_KEEPALIVE_TIME_MS, ge=1000)
    keepalive_timeout_ms: int = Field(default=GRPC_KEEPALIVE_TIMEOUT_MS, ge=1000)
    keepalive_permit_without_calls: bool = Field(
        default=GRPC_KEEPALIVE_PERMIT_WITHOUT_CALLS
    )
    max_pings_without_data: int = Field(default=GRPC_MAX_PINGS_WITHOUT_DATA, ge=0)
    max_connection_idle_ms: int = Field(default=GRPC_MAX_CONNECTION_IDLE_MS, ge=1000)

    # === TLS ===
    use_tls: bool = Field(default=False)
    tls_ca_cert_path: str | None = Field(default=None)
    tls_client_cert_path: str | None = Field(default=None)
    tls_client_key_path: str | None = Field(default=None)
    ssl_target_name_override: str | None = Field(default=None)

    # === Retry ===
    enable_retries: bool = Field(default=GRPC_ENABLE_RETRIES)
    max_retries: int = Field(default=GRPC_MAX_RETRIES, ge=0, le=10)

    # === Message Limits ===
    max_send_message_length: int = Field(default=GRPC_MAX_MESSAGE_LENGTH, ge=1024)
    max_receive_message_length: int = Field(default=GRPC_MAX_MESSAGE_LENGTH, ge=1024)

    # === Compression ===
    compression: Literal["gzip", "deflate"] | None = Field(default=None)

    # === Interceptors ===
    interceptors: list[str] = Field(default_factory=list)

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: str) -> str:
        if not v:
            raise ValueError("Address cannot be empty")
        if ":" not in v:
            raise ValueError(f"Invalid address: {v}. Must be 'host:port'")

        host, port_str = v.rsplit(":", 1)
        if not host:
            raise ValueError(f"Invalid address: {v}. Host cannot be empty")

        try:
            port = int(port_str)
            if not (1 <= port <= 65535):
                raise ValueError(f"Port out of range: {port}. Must be 1-65535")
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError(f"Invalid port in address: {v}")
            raise

        return v

    @field_validator("compression")
    @classmethod
    def validate_compression(cls, v: str | None) -> str | None:
        if v is not None and v not in ("gzip", "deflate"):
            raise ValueError(f"Invalid compression: {v}. Must be 'gzip' or 'deflate'")
        return v

    def get_channel_options(self) -> list[tuple[str, object]]:
        """Get gRPC channel options for aio.insecure_channel/secure_channel."""
        options: list[tuple[str, object]] = [
            ("grpc.keepalive_time_ms", self.keepalive_time_ms),
            ("grpc.keepalive_timeout_ms", self.keepalive_timeout_ms),
            ("grpc.keepalive_permit_without_calls", self.keepalive_permit_without_calls),
            ("grpc.http2.max_pings_without_data", self.max_pings_without_data),
            ("grpc.max_connection_idle_ms", self.max_connection_idle_ms),
            ("grpc.enable_retries", 1 if self.enable_retries else 0),
            ("grpc.max_retry_attempts", self.max_retries),
            ("grpc.max_send_message_length", self.max_send_message_length),
            ("grpc.max_receive_message_length", self.max_receive_message_length),
        ]

        if self.ssl_target_name_override:
            options.append(
                ("grpc.ssl_target_name_override", self.ssl_target_name_override)
            )

        return options

    def get_compression(self) -> "grpc.Compression | None":
        """Get gRPC compression enum value."""
        if self.compression is None:
            return None

        import grpc

        if self.compression == "gzip":
            return grpc.Compression.Gzip
        elif self.compression == "deflate":
            return grpc.Compression.Deflate
        return grpc.Compression.NoCompression

    @property
    def host(self) -> str:
        return self.address.rsplit(":", 1)[0]

    @property
    def port(self) -> int:
        return int(self.address.rsplit(":", 1)[1])

    @classmethod
    def from_host_port(
        cls,
        host: str = GRPC_DEFAULT_HOST,
        port: int = GRPC_DEFAULT_PORT,
        **kwargs: Any,
    ) -> "ClientChannelConfig":
        """Create config from separate host and port."""
        return cls(address=f"{host}:{port}", **kwargs)


__all__ = ["ClientChannelConfig"]
