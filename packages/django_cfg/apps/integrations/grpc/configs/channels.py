"""
gRPC Client Channel Configuration.

This module provides configuration for gRPC client channel creation,
consolidating all channel options that were previously hardcoded.

Usage:
    from django_cfg.apps.integrations.grpc.configs.channels import ClientChannelConfig

    config = ClientChannelConfig(
        address="grpc.example.com:443",
        use_tls=True,
        max_retries=5,
    )

    # Get channel options for grpc.aio.insecure_channel/secure_channel
    options = config.get_channel_options()
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Tuple

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
    import grpc.aio


class ClientChannelConfig(BaseModel):
    """
    Configuration for gRPC client channel creation.

    Consolidates all channel options that were previously hardcoded
    in DynamicGRPCClient and other client implementations.

    Attributes:
        address: Server address in "host:port" format
        wait_for_ready: Wait for channel to be ready before RPC
        connect_timeout: Connection timeout in seconds
        call_timeout: Default RPC call timeout in seconds
        keepalive_time_ms: Keepalive ping interval in milliseconds
        keepalive_timeout_ms: Keepalive ping timeout in milliseconds
        keepalive_permit_without_calls: Allow pings without active calls
        max_pings_without_data: Max pings allowed without data
        max_connection_idle_ms: Close idle connections after (ms)
        use_tls: Use TLS for secure connection
        tls_ca_cert_path: Path to CA certificate
        tls_client_cert_path: Path to client certificate (mTLS)
        tls_client_key_path: Path to client private key (mTLS)
        ssl_target_name_override: Override SSL target name
        enable_retries: Enable automatic retries
        max_retries: Maximum retry attempts
        max_send_message_length: Max outbound message size
        max_receive_message_length: Max inbound message size
        compression: Compression algorithm ('gzip' or 'deflate')
        interceptors: Client interceptor import paths

    Example:
        # Simple insecure connection
        config = ClientChannelConfig(address="localhost:50051")

        # TLS connection with custom timeouts
        config = ClientChannelConfig(
            address="grpc.example.com:443",
            use_tls=True,
            connect_timeout=10.0,
            call_timeout=30.0,
            max_retries=5,
        )

        # Get channel options
        options = config.get_channel_options()
        channel = grpc.aio.insecure_channel(config.address, options=options)
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_assignment=True,
    )

    # === Target ===
    address: str = Field(
        ...,
        description="Server address in 'host:port' format",
    )

    # === Connection Options ===
    wait_for_ready: bool = Field(
        default=True,
        description="Wait for channel to be ready before sending RPCs",
    )
    connect_timeout: float = Field(
        default=GRPC_CONNECT_TIMEOUT,
        gt=0.0,
        le=300.0,
        description="Connection timeout in seconds",
    )
    call_timeout: float = Field(
        default=GRPC_RPC_CALL_TIMEOUT,
        gt=0.0,
        le=600.0,
        description="Default RPC call timeout in seconds",
    )

    # === Keepalive ===
    keepalive_time_ms: int = Field(
        default=GRPC_KEEPALIVE_TIME_MS,
        ge=1000,
        description="Keepalive ping interval in milliseconds",
    )
    keepalive_timeout_ms: int = Field(
        default=GRPC_KEEPALIVE_TIMEOUT_MS,
        ge=1000,
        description="Keepalive ping timeout in milliseconds",
    )
    keepalive_permit_without_calls: bool = Field(
        default=GRPC_KEEPALIVE_PERMIT_WITHOUT_CALLS,
        description="Allow keepalive pings without active calls",
    )
    max_pings_without_data: int = Field(
        default=GRPC_MAX_PINGS_WITHOUT_DATA,
        ge=0,
        description="Maximum pings allowed without data",
    )
    max_connection_idle_ms: int = Field(
        default=GRPC_MAX_CONNECTION_IDLE_MS,
        ge=1000,
        description="Close idle connections after (milliseconds)",
    )

    # === TLS ===
    use_tls: bool = Field(
        default=False,
        description="Use TLS for secure connection",
    )
    tls_ca_cert_path: Optional[str] = Field(
        default=None,
        description="Path to CA certificate for server verification",
    )
    tls_client_cert_path: Optional[str] = Field(
        default=None,
        description="Path to client certificate (for mTLS)",
    )
    tls_client_key_path: Optional[str] = Field(
        default=None,
        description="Path to client private key (for mTLS)",
    )
    ssl_target_name_override: Optional[str] = Field(
        default=None,
        description="Override SSL target name (useful for testing)",
    )

    # === Retry ===
    enable_retries: bool = Field(
        default=GRPC_ENABLE_RETRIES,
        description="Enable automatic retries for failed RPCs",
    )
    max_retries: int = Field(
        default=GRPC_MAX_RETRIES,
        ge=0,
        le=10,
        description="Maximum number of retry attempts",
    )

    # === Message Limits ===
    max_send_message_length: int = Field(
        default=GRPC_MAX_MESSAGE_LENGTH,
        ge=1024,
        description="Maximum outbound message size in bytes",
    )
    max_receive_message_length: int = Field(
        default=GRPC_MAX_MESSAGE_LENGTH,
        ge=1024,
        description="Maximum inbound message size in bytes",
    )

    # === Compression ===
    compression: Optional[str] = Field(
        default=None,
        description="Compression algorithm: 'gzip' or 'deflate'",
    )

    # === Interceptors ===
    interceptors: List[str] = Field(
        default_factory=list,
        description="List of client interceptor import paths",
    )

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: str) -> str:
        """Validate address format is 'host:port'."""
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
    def validate_compression(cls, v: Optional[str]) -> Optional[str]:
        """Validate compression algorithm."""
        if v is not None and v not in ("gzip", "deflate"):
            raise ValueError(f"Invalid compression: {v}. Must be 'gzip' or 'deflate'")
        return v

    def get_channel_options(self) -> List[Tuple[str, any]]:
        """
        Get gRPC channel options for aio.insecure_channel/secure_channel.

        Returns:
            List of (option_name, option_value) tuples suitable for
            passing to grpc.aio.insecure_channel() or grpc.aio.secure_channel().

        Example:
            config = ClientChannelConfig(address="localhost:50051")
            options = config.get_channel_options()
            channel = grpc.aio.insecure_channel(config.address, options=options)
        """
        options = [
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

    def get_compression(self) -> Optional["grpc.Compression"]:
        """
        Get gRPC compression enum value.

        Returns:
            grpc.Compression value or None if no compression.
        """
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
        """Extract host from address."""
        return self.address.rsplit(":", 1)[0]

    @property
    def port(self) -> int:
        """Extract port from address."""
        return int(self.address.rsplit(":", 1)[1])

    @classmethod
    def from_host_port(
        cls,
        host: str = GRPC_DEFAULT_HOST,
        port: int = GRPC_DEFAULT_PORT,
        **kwargs,
    ) -> "ClientChannelConfig":
        """
        Create config from separate host and port.

        Args:
            host: Server hostname or IP
            port: Server port number
            **kwargs: Additional configuration options

        Returns:
            ClientChannelConfig instance

        Example:
            config = ClientChannelConfig.from_host_port(
                host="grpc.example.com",
                port=443,
                use_tls=True,
            )
        """
        return cls(address=f"{host}:{port}", **kwargs)
