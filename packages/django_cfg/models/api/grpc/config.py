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
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator, model_validator

from django_cfg.models.base import BaseConfig

# Import TLSConfig from centralized configs
from django_cfg.apps.integrations.grpc.configs.tls import TLSConfig


class GRPCKeepaliveConfig(BaseConfig):
    """
    gRPC HTTP/2 keepalive configuration.

    Controls HTTP/2 PING frames for connection health and dead connection detection.
    These settings should match between client and server for optimal behavior.

    Recommended settings for long-lived bidirectional streaming:
    - time_ms: 10000 (10s) - fast dead connection detection
    - timeout_ms: 5000 (5s) - quick ping acknowledgment
    - permit_without_calls: True - maintain idle connections
    - max_pings_without_data: 0 - unlimited pings for streaming

    Example:
        >>> config = GRPCKeepaliveConfig(
        ...     time_ms=10000,  # Ping every 10 seconds
        ...     timeout_ms=5000,  # Wait 5 seconds for ACK
        ...     permit_without_calls=True,
        ... )
    """

    time_ms: int = Field(
        default=10000,  # 10 seconds (matches Go client)
        description="Keepalive ping interval in milliseconds. How often to send HTTP/2 PING if no activity.",
        ge=1000,  # Min 1 second
        le=7200000,  # Max 2 hours
    )

    timeout_ms: int = Field(
        default=5000,  # 5 seconds (matches Go client)
        description="Keepalive ping timeout in milliseconds. How long to wait for PING ACK.",
        ge=1000,  # Min 1 second
        le=60000,  # Max 1 minute
    )

    permit_without_calls: bool = Field(
        default=True,
        description="Allow keepalive pings even without active RPC calls. Essential for idle connections.",
    )

    min_time_between_pings_ms: int = Field(
        default=5000,  # 5 seconds
        description="Minimum time between successive pings (anti-abuse protection).",
        ge=1000,
        le=60000,
    )

    max_pings_without_data: int = Field(
        default=0,  # 0 = unlimited (important for streaming)
        description="Maximum pings allowed without data. 0 = unlimited (recommended for streaming).",
        ge=0,
        le=100,
    )

    @classmethod
    def for_streaming(cls) -> "GRPCKeepaliveConfig":
        """
        Factory for long-lived bidirectional streaming connections.

        Optimized for:
        - Fast dead connection detection (10s ping, 5s timeout = 15s detection)
        - Stable connections through NAT/firewalls
        - Unlimited idle pings for streaming
        """
        return cls(
            time_ms=10000,
            timeout_ms=5000,
            permit_without_calls=True,
            min_time_between_pings_ms=5000,
            max_pings_without_data=0,
        )

    @classmethod
    def for_short_lived(cls) -> "GRPCKeepaliveConfig":
        """
        Factory for short-lived RPC connections.

        Optimized for:
        - Less aggressive keepalive
        - Standard anti-abuse protection
        """
        return cls(
            time_ms=30000,
            timeout_ms=10000,
            permit_without_calls=True,
            min_time_between_pings_ms=10000,
            max_pings_without_data=2,
        )

    def to_grpc_options(self) -> list[tuple[str, Any]]:
        """Convert to gRPC server/channel options."""
        return [
            ("grpc.keepalive_time_ms", self.time_ms),
            ("grpc.keepalive_timeout_ms", self.timeout_ms),
            ("grpc.keepalive_permit_without_calls", self.permit_without_calls),
            ("grpc.http2.min_time_between_pings_ms", self.min_time_between_pings_ms),
            ("grpc.http2.min_ping_interval_without_data_ms", self.min_time_between_pings_ms),
            ("grpc.http2.max_pings_without_data", self.max_pings_without_data),
        ]


class GRPCConnectionLimitsConfig(BaseConfig):
    """
    gRPC connection limits configuration.

    Controls connection lifecycle for server-side connection management.

    Example:
        >>> config = GRPCConnectionLimitsConfig(
        ...     max_connection_idle_ms=7200000,  # 2 hours
        ...     max_connection_age_ms=0,  # Unlimited (for streaming)
        ... )
    """

    max_connection_idle_ms: int = Field(
        default=7200000,  # 2 hours
        description="Maximum idle connection time in milliseconds before server closes it.",
        ge=0,  # 0 = unlimited
    )

    max_connection_age_ms: int = Field(
        default=0,  # Unlimited (important for long-lived streaming)
        description="Maximum connection age in milliseconds. 0 = unlimited (recommended for streaming).",
        ge=0,
    )

    max_connection_age_grace_ms: int = Field(
        default=300000,  # 5 minutes
        description="Grace period for in-flight RPCs when connection age limit is reached.",
        ge=0,
    )

    def to_grpc_options(self) -> list[tuple[str, int]]:
        """Convert to gRPC server options."""
        return [
            ("grpc.max_connection_idle_ms", self.max_connection_idle_ms),
            ("grpc.max_connection_age_ms", self.max_connection_age_ms),
            ("grpc.max_connection_age_grace_ms", self.max_connection_age_grace_ms),
        ]


class GRPCServerConfig(BaseConfig):
    """
    gRPC server configuration.

    Configures the gRPC server including host, port, workers, compression,
    message limits, and keepalive settings.

    Example:
        >>> config = GRPCServerConfig(
        ...     host="0.0.0.0",
        ...     port=50051,
        ...     compression="gzip",
        ...     keepalive=GRPCKeepaliveConfig.for_streaming(),
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

    # Nested keepalive config (Pydantic2)
    keepalive: GRPCKeepaliveConfig = Field(
        default_factory=GRPCKeepaliveConfig,
        description="HTTP/2 keepalive settings for connection health",
    )

    # Nested connection limits config (Pydantic2)
    connection_limits: GRPCConnectionLimitsConfig = Field(
        default_factory=GRPCConnectionLimitsConfig,
        description="Connection lifecycle limits",
    )

    interceptors: List[str] = Field(
        default_factory=list,
        description=(
            "Additional custom interceptors (added AFTER built-in interceptors). "
            "Built-in interceptors (auto-added by generator): "
            "ObservabilityInterceptor (metrics, logging, DB logging, Centrifugo) + "
            "ApiKeyAuthInterceptor (if auth.enabled=True). "
            "Example: ['myapp.interceptors.RateLimitInterceptor']"
        ),
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


class GRPCObservabilityConfig(BaseConfig):
    """
    gRPC observability configuration.

    Simple, production-ready defaults. Most users won't need to change anything.

    Example:
        >>> config = GRPCObservabilityConfig(
        ...     log_to_db=False,  # Disable DB logging in high-traffic production
        ...     telegram_notifications=True,  # Enable Telegram notifications
        ...     telegram_exclude_methods=["/grpc.health.v1.Health/Check"],  # Exclude health checks
        ... )
    """

    # === Database Logging (GRPCRequestLog) ===
    log_to_db: bool = Field(
        default=True,
        description="Log requests to database (GRPCRequestLog). Disable for high-traffic production.",
    )

    log_errors_only: bool = Field(
        default=False,
        description="Only log errors to DB (skip successful requests).",
    )

    # === Heartbeat (GRPCServerStatus) ===
    heartbeat_interval: int = Field(
        default=300,
        description="Heartbeat interval in seconds (default 5 min).",
        ge=30,
        le=3600,
    )

    # === Telegram Notifications ===
    telegram_notifications: bool = Field(
        default=False,
        description="Send gRPC request notifications to Telegram (requires Telegram integration configured).",
    )

    telegram_exclude_methods: List[str] = Field(
        default_factory=lambda: [
            "/grpc.health.v1.Health/Check",
            "/grpc.health.v1.Health/Watch",
            "/grpc.reflection.v1alpha.ServerReflection/ServerReflectionInfo",
        ],
        description=(
            "List of gRPC methods to exclude from Telegram notifications in production. "
            "In development mode (env_mode=DEVELOPMENT), these methods ARE allowed for debugging."
        ),
    )

    # === Centrifugo Integration ===
    centrifugo_publish_start: bool = Field(
        default=False,
        description="Publish gRPC request start events to Centrifugo",
    )

    centrifugo_publish_end: bool = Field(
        default=True,
        description="Publish gRPC request end events to Centrifugo",
    )

    centrifugo_publish_errors: bool = Field(
        default=True,
        description="Publish gRPC errors to Centrifugo",
    )

    centrifugo_publish_stream_messages: bool = Field(
        default=False,
        description="Publish individual streaming messages to Centrifugo (can be verbose)",
    )

    centrifugo_channel_template: str = Field(
        default="grpc:{service}:{method}:meta",
        description="Centrifugo channel template for gRPC events. Supports {service}, {method} placeholders.",
    )

    centrifugo_error_channel_template: str = Field(
        default="grpc:{service}:{method}:errors",
        description="Centrifugo channel template for gRPC errors. Supports {service}, {method} placeholders.",
    )

    centrifugo_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata to include in Centrifugo publishes",
    )


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

    internal_url: Optional[str] = Field(
        default=None,
        description="Internal Docker/Kubernetes URL for container-to-container communication (e.g., 'djangocfg-grpc:50051' or 'localhost:50051')",
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

    observability: GRPCObservabilityConfig = Field(
        default_factory=GRPCObservabilityConfig,
        description="Observability configuration: logging, metrics, DB tracking (optional)",
    )

    tls: TLSConfig = Field(
        default_factory=TLSConfig,
        description="TLS/SSL configuration for secure connections (optional)",
    )

    # === Flatten TLS Config (most common settings) ===
    tls_enabled: Optional[bool] = Field(
        default=None,
        description="Enable TLS/SSL for secure connections. If None, uses tls.enabled (False by default)",
    )

    tls_cert_path: Optional[str] = Field(
        default=None,
        description="Path to server certificate file. If None, uses tls.cert_path",
    )

    tls_key_path: Optional[str] = Field(
        default=None,
        description="Path to server private key file. If None, uses tls.key_path",
    )

    handlers_hook: str | List[str] = Field(
        default="",
        description="Import path(s) to grpc_handlers function (optional, e.g., '{ROOT_URLCONF}.grpc_handlers' or list of paths)",
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

        # Apply flatten TLS fields to nested tls config
        # Note: TLSConfig is frozen, so we need to create a new instance
        if self.tls_enabled is not None or self.tls_cert_path is not None or self.tls_key_path is not None:
            tls_kwargs = {
                "enabled": self.tls_enabled if self.tls_enabled is not None else self.tls.enabled,
                "cert_path": self.tls_cert_path if self.tls_cert_path is not None else self.tls.cert_path,
                "key_path": self.tls_key_path if self.tls_key_path is not None else self.tls.key_path,
                "ca_cert_path": self.tls.ca_cert_path,
                "client_cert_path": self.tls.client_cert_path,
                "client_key_path": self.tls.client_key_path,
                "require_client_cert": self.tls.require_client_cert,
                "verify_server": self.tls.verify_server,
                "min_version": self.tls.min_version,
                "ssl_target_name_override": self.tls.ssl_target_name_override,
            }
            self.tls = TLSConfig(**tls_kwargs)

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
