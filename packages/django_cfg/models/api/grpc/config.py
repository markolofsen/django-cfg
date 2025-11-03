"""
gRPC Configuration Models

Type-safe Pydantic v2 models for gRPC server, authentication, and proto generation.

Example:
    >>> from django_cfg.models.api.grpc import GRPCConfig
    >>> config = GRPCConfig(
    ...     enabled=True,
    ...     server=GRPCServerConfig(port=50051),
    ...     auth=GRPCAuthConfig(require_auth=True)
    ... )
"""

import warnings
from typing import Dict, List, Optional

from pydantic import Field, field_validator, model_validator

from django_cfg.models.base import BaseConfig


class GRPCServerConfig(BaseConfig):
    """
    gRPC server configuration.

    Configures the gRPC server including host, port, workers, compression,
    message limits, and keepalive settings.

    Example:
        >>> config = GRPCServerConfig(
        ...     host="0.0.0.0",
        ...     port=50051,
        ...     max_workers=10,
        ...     compression="gzip"
        ... )
    """

    enabled: bool = Field(
        default=True,
        description="Enable gRPC server",
    )

    host: str = Field(
        default="[::]",
        description="Server bind address (IPv6 by default, use 0.0.0.0 for IPv4)",
    )

    port: int = Field(
        default=50051,
        description="Server port",
        ge=1024,
        le=65535,
    )

    max_workers: int = Field(
        default=10,
        description="ThreadPoolExecutor max workers",
        ge=1,
        le=1000,
    )

    enable_reflection: bool = Field(
        default=False,
        description="Enable server reflection for dynamic clients (grpcurl, etc.)",
    )

    enable_health_check: bool = Field(
        default=True,
        description="Enable gRPC health check service",
    )

    compression: Optional[str] = Field(
        default=None,
        description="Compression algorithm: 'gzip', 'deflate', or None",
    )

    max_send_message_length: int = Field(
        default=4 * 1024 * 1024,  # 4 MB
        description="Maximum outbound message size in bytes",
        ge=1024,  # Min 1KB
        le=100 * 1024 * 1024,  # Max 100MB
    )

    max_receive_message_length: int = Field(
        default=4 * 1024 * 1024,  # 4 MB
        description="Maximum inbound message size in bytes",
        ge=1024,
        le=100 * 1024 * 1024,
    )

    keepalive_time_ms: int = Field(
        default=7200000,  # 2 hours
        description="Keepalive ping interval in milliseconds",
        ge=1000,  # Min 1 second
    )

    keepalive_timeout_ms: int = Field(
        default=20000,  # 20 seconds
        description="Keepalive ping timeout in milliseconds",
        ge=1000,
    )

    interceptors: List[str] = Field(
        default_factory=list,
        description="Server interceptor import paths (e.g., 'myapp.interceptors.AuthInterceptor')",
    )

    @field_validator("compression")
    @classmethod
    def validate_compression(cls, v: Optional[str]) -> Optional[str]:
        """Validate compression algorithm."""
        if v and v not in ("gzip", "deflate"):
            raise ValueError(
                f"Invalid compression: {v}. Must be 'gzip', 'deflate', or None"
            )
        return v

    @field_validator("host")
    @classmethod
    def validate_host(cls, v: str) -> str:
        """Validate host format."""
        if not v or not v.strip():
            raise ValueError("Host cannot be empty")
        return v.strip()


class GRPCAuthConfig(BaseConfig):
    """
    gRPC authentication configuration.

    Supports JWT authentication with configurable token handling.

    Example:
        >>> config = GRPCAuthConfig(
        ...     enabled=True,
        ...     require_auth=True,
        ...     jwt_algorithm="HS256"
        ... )
    """

    enabled: bool = Field(
        default=True,
        description="Enable authentication",
    )

    require_auth: bool = Field(
        default=True,
        description="Require authentication for all services (except public_methods)",
    )

    token_header: str = Field(
        default="authorization",
        description="Metadata key for auth token",
    )

    token_prefix: str = Field(
        default="Bearer",
        description="Token prefix (e.g., 'Bearer' for JWT)",
    )

    jwt_secret_key: Optional[str] = Field(
        default=None,
        description="JWT secret key (defaults to Django SECRET_KEY if None)",
    )

    jwt_algorithm: str = Field(
        default="HS256",
        description="JWT signing algorithm",
    )

    jwt_verify_exp: bool = Field(
        default=True,
        description="Verify JWT expiration",
    )

    jwt_leeway: int = Field(
        default=0,
        description="JWT expiration leeway in seconds",
        ge=0,
    )

    public_methods: List[str] = Field(
        default_factory=lambda: [
            "/grpc.health.v1.Health/Check",
            "/grpc.health.v1.Health/Watch",
        ],
        description="RPC methods that don't require authentication",
    )

    @field_validator("jwt_algorithm")
    @classmethod
    def validate_jwt_algorithm(cls, v: str) -> str:
        """Validate JWT algorithm."""
        valid_algorithms = {
            "HS256",
            "HS384",
            "HS512",
            "RS256",
            "RS384",
            "RS512",
            "ES256",
            "ES384",
            "ES512",
        }
        if v not in valid_algorithms:
            raise ValueError(
                f"Invalid JWT algorithm: {v}. "
                f"Must be one of: {', '.join(sorted(valid_algorithms))}"
            )
        return v


class GRPCProtoConfig(BaseConfig):
    """
    Proto file generation configuration.

    Controls automatic proto file generation from Django models.

    Example:
        >>> config = GRPCProtoConfig(
        ...     auto_generate=True,
        ...     output_dir="protos",
        ...     package_prefix="mycompany"
        ... )
    """

    auto_generate: bool = Field(
        default=True,
        description="Auto-generate proto files from Django models",
    )

    output_dir: str = Field(
        default="protos",
        description="Proto files output directory (relative to BASE_DIR)",
    )

    package_prefix: str = Field(
        default="",
        description="Package prefix for all generated protos (e.g., 'mycompany')",
    )

    include_services: bool = Field(
        default=True,
        description="Include service definitions in generated protos",
    )

    field_naming: str = Field(
        default="snake_case",
        description="Proto field naming convention",
    )

    @field_validator("field_naming")
    @classmethod
    def validate_field_naming(cls, v: str) -> str:
        """Validate field naming convention."""
        if v not in ("snake_case", "camelCase"):
            raise ValueError(
                f"Invalid field_naming: {v}. Must be 'snake_case' or 'camelCase'"
            )
        return v

    @field_validator("output_dir")
    @classmethod
    def validate_output_dir(cls, v: str) -> str:
        """Validate output directory."""
        if not v or not v.strip():
            raise ValueError("output_dir cannot be empty")
        # Remove leading/trailing slashes
        return v.strip().strip("/")


class GRPCConfig(BaseConfig):
    """
    Main gRPC configuration.

    Combines server, authentication, and proto generation settings.

    Example:
        Basic setup:
        >>> config = GRPCConfig(enabled=True)

        Advanced setup:
        >>> config = GRPCConfig(
        ...     enabled=True,
        ...     server=GRPCServerConfig(port=8080, max_workers=50),
        ...     auth=GRPCAuthConfig(require_auth=True),
        ...     auto_register_apps=["accounts", "support"]
        ... )
    """

    enabled: bool = Field(
        default=False,
        description="Enable gRPC integration",
    )

    server: GRPCServerConfig = Field(
        default_factory=GRPCServerConfig,
        description="Server configuration",
    )

    auth: GRPCAuthConfig = Field(
        default_factory=GRPCAuthConfig,
        description="Authentication configuration",
    )

    proto: GRPCProtoConfig = Field(
        default_factory=GRPCProtoConfig,
        description="Proto generation configuration",
    )

    handlers_hook: str = Field(
        default="",
        description="Import path to grpc_handlers function (optional, e.g., '{ROOT_URLCONF}.grpc_handlers')",
    )

    auto_register_apps: bool = Field(
        default=True,
        description="Auto-register gRPC services for Django-CFG apps",
    )

    enabled_apps: List[str] = Field(
        default_factory=lambda: [
            "accounts",
            "support",
            "knowbase",
            "agents",
            "payments",
            "leads",
        ],
        description="Django-CFG apps to expose via gRPC (if auto_register_apps=True)",
    )

    custom_services: Dict[str, str] = Field(
        default_factory=dict,
        description="Custom service import paths: {service_name: 'path.to.Service'}",
    )

    @model_validator(mode="after")
    def validate_grpc_config(self) -> "GRPCConfig":
        """Cross-field validation."""
        # Check dependencies if enabled
        if self.enabled:
            from django_cfg.apps.integrations.grpc._cfg import require_grpc_feature

            require_grpc_feature()

            # Validate server enabled
            if not self.server.enabled:
                raise ValueError(
                    "Cannot enable gRPC with server disabled. "
                    "Set server.enabled=True or grpc.enabled=False"
                )

        # Warn if auto_register but no apps
        if self.auto_register_apps and not self.enabled_apps:
            warnings.warn(
                "auto_register_apps is True but enabled_apps is empty. "
                "No services will be auto-registered.",
                UserWarning,
                stacklevel=2,
            )

        return self
