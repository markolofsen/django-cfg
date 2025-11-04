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

    max_concurrent_streams: Optional[int] = Field(
        default=None,
        description="Max concurrent streams per connection (None = unlimited, async server)",
        ge=1,
        le=10000,
    )

    asyncio_debug: bool = Field(
        default=False,
        description="Enable asyncio debug mode (shows async warnings and coroutine leaks)",
    )

    enable_reflection: bool = Field(
        default=True,
        description="Enable server reflection for grpcurl and other tools (enabled by default)",
    )

    enable_health_check: bool = Field(
        default=True,
        description="Enable gRPC health check service",
    )

    public_url: Optional[str] = Field(
        default=None,
        description="Public URL for clients (auto-generated from api_url if None)",
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

    @model_validator(mode="after")
    def auto_set_smart_defaults(self) -> "GRPCServerConfig":
        """Auto-set smart defaults based on Django settings."""
        try:
            from django_cfg.core import get_current_config
            config = get_current_config()

            if config:
                # Auto-set public_url from api_url
                if self.public_url is None and hasattr(config, 'api_url') and config.api_url:
                    # https://api.djangocfg.com → grpc.djangocfg.com:50051
                    url = config.api_url
                    url = url.replace("https://", "").replace("http://", "")
                    url = url.replace("api.", "grpc.")
                    # Remove trailing slash
                    url = url.rstrip("/")
                    self.public_url = f"{url}:{self.port}"

                # Auto-enable asyncio_debug in development mode
                # Check if already explicitly set (if user set it, don't override)
                # Only auto-enable if env_mode is development/local/dev
                if hasattr(config, 'env_mode'):
                    is_dev = config.env_mode in ("local", "development", "dev")
                    # Only auto-enable if not explicitly set to False
                    # We check if it's still the default value (False) and enable it in dev
                    if is_dev and not self.asyncio_debug:
                        # Check Django DEBUG setting as fallback
                        try:
                            from django.conf import settings
                            if hasattr(settings, 'DEBUG') and settings.DEBUG:
                                self.asyncio_debug = True
                        except:
                            # If Django not configured yet, just use env_mode
                            self.asyncio_debug = True

        except Exception:
            # Config not available yet
            pass

        return self


class GRPCAuthConfig(BaseConfig):
    """
    gRPC authentication configuration.

    Uses API key authentication with Django ORM for secure, manageable access control.

    Example:
        >>> config = GRPCAuthConfig(
        ...     enabled=True,
        ...     require_auth=False,
        ...     accept_django_secret_key=True,
        ... )
    """

    enabled: bool = Field(
        default=True,
        description="Enable authentication",
    )

    require_auth: bool = Field(
        default=False,  # Smart default: easy development
        description="Require authentication for all services (except public_methods)",
    )

    # === API Key Authentication ===
    api_key_header: str = Field(
        default="x-api-key",
        description="Metadata header name for API key (default: x-api-key)",
    )

    accept_django_secret_key: bool = Field(
        default=True,  # Smart default: SECRET_KEY works for development
        description="Accept Django SECRET_KEY as valid API key (for development/internal use)",
    )

    # === Public Methods ===
    public_methods: List[str] = Field(
        default_factory=lambda: [
            "/grpc.health.v1.Health/Check",
            "/grpc.health.v1.Health/Watch",
            "/grpc.reflection.v1alpha.ServerReflection/ServerReflectionInfo",
        ],
        description="RPC methods that don't require authentication",
    )


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

    output_dir: Optional[str] = Field(
        default=None,
        description="Proto files output directory (auto: media/protos if None)",
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
    def validate_output_dir(cls, v: Optional[str]) -> Optional[str]:
        """Validate output directory."""
        if v is None:
            return None
        if not v.strip():
            raise ValueError("output_dir cannot be empty string")
        # Remove leading/trailing slashes
        return v.strip().strip("/")

    @model_validator(mode="after")
    def auto_set_output_dir(self) -> "GRPCProtoConfig":
        """Auto-set output_dir to media/protos if not specified."""
        if self.output_dir is None:
            # Better default: generated files go to media
            self.output_dir = "media/protos"
        return self


class GRPCConfig(BaseConfig):
    """
    Main gRPC configuration.

    Combines server, authentication, and proto generation settings.

    Example:
        Simple flat API (recommended):
        >>> config = GRPCConfig(
        ...     enabled=True,
        ...     enabled_apps=["crypto"],
        ...     package_prefix="api",
        ... )

        Advanced with nested configs (optional):
        >>> config = GRPCConfig(
        ...     enabled=True,
        ...     server=GRPCServerConfig(port=8080, max_workers=50),
        ...     auth=GRPCAuthConfig(require_auth=True),
        ...     enabled_apps=["accounts", "support"]
        ... )
    """

    enabled: bool = Field(
        default=False,
        description="Enable gRPC integration",
    )

    # === Flatten Server Config (most common settings) ===
    # These are shortcuts that configure the nested server config
    host: Optional[str] = Field(
        default=None,
        description="Server bind address (e.g., '[::]' for IPv6, '0.0.0.0' for IPv4). If None, uses server.host default",
    )

    port: Optional[int] = Field(
        default=None,
        description="Server port (e.g., 50051). If None, uses server.port default",
        ge=1024,
        le=65535,
    )

    public_url: Optional[str] = Field(
        default=None,
        description="Public URL for clients (e.g., 'grpc.djangocfg.com:443'). If None, auto-generated from api_url",
    )

    enable_reflection: Optional[bool] = Field(
        default=None,
        description="Enable server reflection for grpcurl/tools. If None, uses server.enable_reflection (True by default)",
    )

    # === Flatten Proto Config (most common settings) ===
    package_prefix: Optional[str] = Field(
        default=None,
        description="Package prefix for proto files (e.g., 'api'). If None, uses proto.package_prefix default",
    )

    output_dir: Optional[str] = Field(
        default=None,
        description="Proto files output directory. If None, uses proto.output_dir default (media/protos)",
    )

    # === Nested Configs (for advanced use) ===
    server: GRPCServerConfig = Field(
        default_factory=GRPCServerConfig,
        description="Advanced server configuration (optional, use flatten fields above for common settings)",
    )

    auth: GRPCAuthConfig = Field(
        default_factory=GRPCAuthConfig,
        description="Authentication configuration (optional)",
    )

    proto: GRPCProtoConfig = Field(
        default_factory=GRPCProtoConfig,
        description="Proto generation configuration (optional, use flatten fields above for common settings)",
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
        """
        Cross-field validation and apply flatten fields to nested configs.

        This allows users to configure common settings at the top level without
        importing nested config classes.
        """
        # Apply flatten server fields to nested server config
        if self.host is not None:
            self.server.host = self.host
        if self.port is not None:
            self.server.port = self.port
        if self.public_url is not None:
            self.server.public_url = self.public_url
        if self.enable_reflection is not None:
            self.server.enable_reflection = self.enable_reflection

        # Apply flatten proto fields to nested proto config
        if self.package_prefix is not None:
            self.proto.package_prefix = self.package_prefix
        if self.output_dir is not None:
            self.proto.output_dir = self.output_dir

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
