"""
django_grpc.config.tls — TLS/SSL configuration for gRPC connections.

Supports server-side TLS, client-side TLS, and mutual TLS (mTLS).

Usage:
    from django_cfg.modules.django_grpc.config.tls import TLSConfig

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
from typing import TYPE_CHECKING, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

if TYPE_CHECKING:
    import grpc


class TLSConfig(BaseModel):
    """TLS/SSL configuration for secure gRPC connections."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    # === Enable/Disable ===
    enabled: bool = Field(default=False)

    # === Server Certificates ===
    cert_path: str | None = Field(default=None)
    key_path: str | None = Field(default=None)

    # === Client/CA Certificates ===
    ca_cert_path: str | None = Field(default=None)
    client_cert_path: str | None = Field(default=None)
    client_key_path: str | None = Field(default=None)

    # === Options ===
    require_client_cert: bool = Field(default=False)
    verify_server: bool = Field(default=True)
    min_version: Literal["TLS1.0", "TLS1.1", "TLS1.2", "TLS1.3"] = Field(
        default="TLS1.2",
        description=(
            "Advisory only — gRPC does not expose a TLS version API. "
            "Enforce via GRPC_SSL_CIPHER_SUITES env var or system OpenSSL config. "
            "This field is stored for documentation purposes only (I-7)."
        ),
    )
    ssl_target_name_override: str | None = Field(
        default=None,
        description=(
            "Client-side only. Has no effect when TLSConfig is used with "
            "get_server_credentials(). Used by DynamicGRPCClient and "
            "AsyncResilientGRPCClient to override SNI hostname verification (I-7)."
        ),
    )

    @field_validator(
        "cert_path", "key_path", "ca_cert_path", "client_cert_path", "client_key_path"
    )
    @classmethod
    def validate_path_exists(cls, v: str | None) -> str | None:
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
        valid_versions = ("TLS1.0", "TLS1.1", "TLS1.2", "TLS1.3")
        if v not in valid_versions:
            raise ValueError(
                f"Invalid TLS version: {v}. Must be one of {valid_versions}"
            )
        return v

    @model_validator(mode="after")
    def validate_cert_pairs(self) -> Self:
        if self.enabled:
            if self.cert_path and not self.key_path:
                raise ValueError("key_path is required when cert_path is provided")
            if self.key_path and not self.cert_path:
                raise ValueError("cert_path is required when key_path is provided")
            if self.client_cert_path and not self.client_key_path:
                raise ValueError(
                    "client_key_path is required when client_cert_path is provided"
                )
            if self.client_key_path and not self.client_cert_path:
                raise ValueError(
                    "client_cert_path is required when client_key_path is provided"
                )

            # I-2 fix: mTLS silent downgrade prevention.
            # grpc.ssl_server_credentials() with root_certificates=None silently
            # disables client cert verification even when require_client_auth=True.
            # Fail at config construction time so the operator sees the error immediately.
            if self.require_client_cert and not self.ca_cert_path:
                raise ValueError(
                    "ca_cert_path is required when require_client_cert=True. "
                    "Without it, root_certificates=None is passed to gRPC which "
                    "silently disables client certificate verification — "
                    "mTLS silently degrades to one-way TLS."
                )
        return self

    def _read_file(self, path: str) -> bytes:
        with open(path, "rb") as f:
            return f.read()

    def get_server_credentials(self) -> "grpc.ServerCredentials | None":
        """Get gRPC server credentials for secure server."""
        import grpc

        if not self.enabled or not self.cert_path or not self.key_path:
            return None

        private_key = self._read_file(self.key_path)
        certificate_chain = self._read_file(self.cert_path)
        root_certs = self._read_file(self.ca_cert_path) if self.ca_cert_path else None

        return grpc.ssl_server_credentials(
            [(private_key, certificate_chain)],
            root_certificates=root_certs,
            require_client_auth=self.require_client_cert,
        )

    def get_channel_credentials(self) -> "grpc.ChannelCredentials | None":
        """Get gRPC channel credentials for secure client channel."""
        import grpc

        if not self.enabled:
            return None

        root_certs = self._read_file(self.ca_cert_path) if self.ca_cert_path else None
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

    def get_channel_options(self) -> list[tuple[str, str]]:
        """Get additional channel options for TLS."""
        options = []
        if self.ssl_target_name_override:
            options.append(
                ("grpc.ssl_target_name_override", self.ssl_target_name_override)
            )
        return options

    @property
    def is_mtls(self) -> bool:
        return bool(self.client_cert_path and self.client_key_path)

    @property
    def has_server_certs(self) -> bool:
        return bool(self.cert_path and self.key_path)

    @property
    def has_ca_cert(self) -> bool:
        return bool(self.ca_cert_path)


__all__ = ["TLSConfig"]
