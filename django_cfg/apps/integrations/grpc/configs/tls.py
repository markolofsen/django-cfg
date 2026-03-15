"""
TLS/SSL Configuration for gRPC connections.

This module provides comprehensive TLS configuration for both server and client
gRPC connections, including support for mutual TLS (mTLS).

Usage:
    from django_cfg.apps.integrations.grpc.configs.tls import TLSConfig

    # Server TLS
    server_tls = TLSConfig(
        enabled=True,
        cert_path="/etc/ssl/server.crt",
        key_path="/etc/ssl/server.key",
    )

    # Client with mTLS
    client_tls = TLSConfig(
        enabled=True,
        ca_cert_path="/etc/ssl/ca.crt",
        client_cert_path="/etc/ssl/client.crt",
        client_key_path="/etc/ssl/client.key",
    )
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

if TYPE_CHECKING:
    import grpc


class TLSConfig(BaseModel):
    """
    TLS/SSL configuration for secure gRPC connections.

    Supports:
    - Server-side TLS (cert + key)
    - Client-side TLS (CA cert verification)
    - Mutual TLS (client cert + key for authentication)

    Attributes:
        enabled: Enable TLS/SSL for the connection
        cert_path: Path to server certificate (.crt or .pem)
        key_path: Path to server private key (.key or .pem)
        ca_cert_path: Path to CA certificate for verification
        client_cert_path: Path to client certificate (for mTLS)
        client_key_path: Path to client private key (for mTLS)
        require_client_cert: Require client certificate (server-side mTLS)
        verify_server: Verify server certificate (client-side)
        min_version: Minimum TLS version (TLS1.0, TLS1.1, TLS1.2, TLS1.3)
        ssl_target_name_override: Override target name for SSL verification

    Example:
        # Simple server TLS
        config = TLSConfig(
            enabled=True,
            cert_path="/etc/ssl/certs/server.crt",
            key_path="/etc/ssl/private/server.key",
        )

        # Client connecting to TLS server
        config = TLSConfig(
            enabled=True,
            ca_cert_path="/etc/ssl/certs/ca-bundle.crt",
        )

        # Mutual TLS (both sides authenticate)
        config = TLSConfig(
            enabled=True,
            ca_cert_path="/etc/ssl/certs/ca.crt",
            client_cert_path="/etc/ssl/certs/client.crt",
            client_key_path="/etc/ssl/private/client.key",
            require_client_cert=True,
        )
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_assignment=True,
    )

    # === Enable/Disable ===
    enabled: bool = Field(
        default=False,
        description="Enable TLS/SSL for the connection",
    )

    # === Server Certificates ===
    cert_path: Optional[str] = Field(
        default=None,
        description="Path to server certificate (.crt or .pem)",
    )
    key_path: Optional[str] = Field(
        default=None,
        description="Path to server private key (.key or .pem)",
    )

    # === Client/CA Certificates ===
    ca_cert_path: Optional[str] = Field(
        default=None,
        description="Path to CA certificate for server verification",
    )
    client_cert_path: Optional[str] = Field(
        default=None,
        description="Path to client certificate (for mTLS)",
    )
    client_key_path: Optional[str] = Field(
        default=None,
        description="Path to client private key (for mTLS)",
    )

    # === Options ===
    require_client_cert: bool = Field(
        default=False,
        description="Require client certificate for server-side mTLS",
    )
    verify_server: bool = Field(
        default=True,
        description="Verify server certificate on client-side",
    )
    min_version: str = Field(
        default="TLS1.2",
        description="Minimum TLS version (TLS1.0, TLS1.1, TLS1.2, TLS1.3)",
    )
    ssl_target_name_override: Optional[str] = Field(
        default=None,
        description="Override target name for SSL verification (useful for testing)",
    )

    @field_validator(
        "cert_path", "key_path", "ca_cert_path", "client_cert_path", "client_key_path"
    )
    @classmethod
    def validate_path_exists(cls, v: Optional[str]) -> Optional[str]:
        """Validate that certificate/key paths exist."""
        if v is not None:
            path = Path(v)
            if not path.exists():
                raise ValueError(f"Certificate/key path does not exist: {v}")
            if not path.is_file():
                raise ValueError(f"Path is not a file: {v}")
        return v

    @field_validator("min_version")
    @classmethod
    def validate_tls_version(cls, v: str) -> str:
        """Validate TLS version string."""
        valid_versions = ("TLS1.0", "TLS1.1", "TLS1.2", "TLS1.3")
        if v not in valid_versions:
            raise ValueError(
                f"Invalid TLS version: {v}. Must be one of {valid_versions}"
            )
        return v

    @model_validator(mode="after")
    def validate_cert_pairs(self) -> "TLSConfig":
        """Ensure certificate and key pairs are provided together."""
        if self.enabled:
            # Server requires both cert and key
            if self.cert_path and not self.key_path:
                raise ValueError("key_path is required when cert_path is provided")
            if self.key_path and not self.cert_path:
                raise ValueError("cert_path is required when key_path is provided")

            # Client mTLS requires both client cert and key
            if self.client_cert_path and not self.client_key_path:
                raise ValueError(
                    "client_key_path is required when client_cert_path is provided"
                )
            if self.client_key_path and not self.client_cert_path:
                raise ValueError(
                    "client_cert_path is required when client_key_path is provided"
                )
        return self

    def _read_file(self, path: str) -> bytes:
        """Read file contents as bytes."""
        with open(path, "rb") as f:
            return f.read()

    def get_server_credentials(self) -> Optional["grpc.ServerCredentials"]:
        """
        Get gRPC server credentials for secure server.

        Returns:
            grpc.ServerCredentials if TLS is enabled and configured,
            None otherwise.

        Raises:
            ImportError: If grpc module is not available.
            FileNotFoundError: If certificate files don't exist.

        Example:
            config = TLSConfig(
                enabled=True,
                cert_path="/etc/ssl/server.crt",
                key_path="/etc/ssl/server.key",
            )
            credentials = config.get_server_credentials()
            server.add_secure_port("[::]:50051", credentials)
        """
        import grpc

        if not self.enabled:
            return None

        if not self.cert_path or not self.key_path:
            return None

        private_key = self._read_file(self.key_path)
        certificate_chain = self._read_file(self.cert_path)

        root_certs = None
        if self.ca_cert_path:
            root_certs = self._read_file(self.ca_cert_path)

        return grpc.ssl_server_credentials(
            [(private_key, certificate_chain)],
            root_certificates=root_certs,
            require_client_auth=self.require_client_cert,
        )

    def get_channel_credentials(self) -> Optional["grpc.ChannelCredentials"]:
        """
        Get gRPC channel credentials for secure client channel.

        Returns:
            grpc.ChannelCredentials if TLS is enabled,
            None otherwise.

        Raises:
            ImportError: If grpc module is not available.
            FileNotFoundError: If certificate files don't exist.

        Example:
            config = TLSConfig(
                enabled=True,
                ca_cert_path="/etc/ssl/ca.crt",
            )
            credentials = config.get_channel_credentials()
            channel = grpc.secure_channel("localhost:50051", credentials)
        """
        import grpc

        if not self.enabled:
            return None

        root_certs = None
        if self.ca_cert_path:
            root_certs = self._read_file(self.ca_cert_path)

        private_key = None
        certificate_chain = None
        if self.client_cert_path and self.client_key_path:
            private_key = self._read_file(self.client_key_path)
            certificate_chain = self._read_file(self.client_cert_path)

        return grpc.ssl_channel_credentials(
            root_certificates=root_certs,
            private_key=private_key,
            certificate_chain=certificate_chain,
        )

    def get_channel_options(self) -> list[Tuple[str, str]]:
        """
        Get additional channel options for TLS.

        Returns:
            List of (option_name, option_value) tuples.
        """
        options = []
        if self.ssl_target_name_override:
            options.append(
                ("grpc.ssl_target_name_override", self.ssl_target_name_override)
            )
        return options

    @property
    def is_mtls(self) -> bool:
        """Check if mutual TLS is configured."""
        return bool(self.client_cert_path and self.client_key_path)

    @property
    def has_server_certs(self) -> bool:
        """Check if server certificates are configured."""
        return bool(self.cert_path and self.key_path)

    @property
    def has_ca_cert(self) -> bool:
        """Check if CA certificate is configured."""
        return bool(self.ca_cert_path)
