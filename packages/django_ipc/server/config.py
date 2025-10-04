"""
WebSocket Server Configuration.

Pydantic 2 models for configuring the WebSocket server with type-safety.

File size: ~300 lines
"""

from typing import Optional, Set
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class LogLevel(str, Enum):
    """Logging level."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AuthMode(str, Enum):
    """Authentication mode."""
    NONE = "none"           # No authentication
    JWT = "jwt"             # JWT token
    TOKEN = "token"         # Simple token
    CUSTOM = "custom"       # Custom authentication


class WSServerConfig(BaseModel):
    """
    WebSocket Server configuration.

    All settings for the WebSocket server with sensible defaults.

    Example:
        >>> config = WSServerConfig(
        ...     host="0.0.0.0",
        ...     port=8765,
        ...     redis_url="redis://localhost:6379/2",
        ... )
    """

    # Server settings
    host: str = Field(
        default="0.0.0.0",
        description="Server host to bind to",
    )

    port: int = Field(
        default=8765,
        ge=1024,
        le=65535,
        description="Server port",
    )

    # Redis settings
    redis_url: str = Field(
        default="redis://localhost:6379/2",
        description="Redis connection URL",
    )

    redis_max_connections: int = Field(
        default=50,
        ge=10,
        le=500,
        description="Maximum Redis connections in pool",
    )

    # RPC Bridge settings
    request_stream: str = Field(
        default="stream:requests",
        description="Redis Stream name for RPC requests from Django",
    )

    consumer_group: str = Field(
        default="rpc_group",
        description="Consumer group name",
    )

    consumer_name: Optional[str] = Field(
        default=None,
        description="Consumer name (auto-generated if None)",
    )

    # WebSocket settings
    max_connections: int = Field(
        default=10000,
        ge=100,
        le=100000,
        description="Maximum concurrent WebSocket connections",
    )

    ping_interval: int = Field(
        default=20,
        ge=5,
        le=300,
        description="WebSocket ping interval (seconds)",
    )

    ping_timeout: int = Field(
        default=10,
        ge=5,
        le=60,
        description="WebSocket ping timeout (seconds)",
    )

    max_message_size: int = Field(
        default=1024 * 1024,  # 1MB
        ge=1024,
        le=10 * 1024 * 1024,  # 10MB max
        description="Maximum message size (bytes)",
    )

    # Authentication
    auth_mode: AuthMode = Field(
        default=AuthMode.JWT,
        description="Authentication mode",
    )

    jwt_secret: Optional[str] = Field(
        default=None,
        description="JWT secret key (required if auth_mode=jwt)",
    )

    jwt_algorithm: str = Field(
        default="HS256",
        description="JWT algorithm",
    )

    allowed_tokens: Set[str] = Field(
        default_factory=set,
        description="Allowed tokens (if auth_mode=token)",
    )

    # Logging
    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        description="Logging level",
    )

    log_connections: bool = Field(
        default=True,
        description="Log connection events",
    )

    log_messages: bool = Field(
        default=False,
        description="Log all messages (verbose)",
    )

    # Performance
    enable_compression: bool = Field(
        default=True,
        description="Enable WebSocket compression",
    )

    # Health check
    enable_health_endpoint: bool = Field(
        default=True,
        description="Enable HTTP health check endpoint",
    )

    health_port: int = Field(
        default=8766,
        ge=1024,
        le=65535,
        description="Health check HTTP port",
    )

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, v, info):
        """Validate JWT secret is provided when auth_mode is JWT."""
        auth_mode = info.data.get("auth_mode")
        if auth_mode == AuthMode.JWT and not v:
            raise ValueError("jwt_secret is required when auth_mode=jwt")
        return v

    @field_validator("redis_url")
    @classmethod
    def validate_redis_url(cls, v):
        """Validate Redis URL format."""
        if not v.startswith(("redis://", "rediss://")):
            raise ValueError("redis_url must start with redis:// or rediss://")
        return v

    def get_consumer_name(self, server_id: str) -> str:
        """
        Get consumer name (auto-generate if not set).

        Args:
            server_id: Unique server identifier

        Returns:
            Consumer name
        """
        return self.consumer_name or f"ws_server_{server_id}"


class HandlerConfig(BaseModel):
    """
    Configuration for built-in handlers.

    Example:
        >>> config = HandlerConfig(
        ...     enable_notifications=True,
        ...     enable_broadcasts=True,
        ... )
    """

    # Enable/disable built-in handlers
    enable_notifications: bool = Field(
        default=True,
        description="Enable notification handler",
    )

    enable_broadcasts: bool = Field(
        default=True,
        description="Enable broadcast handler",
    )

    enable_presence: bool = Field(
        default=True,
        description="Enable presence handler",
    )

    # Notification settings
    notification_queue_size: int = Field(
        default=1000,
        ge=100,
        le=10000,
        description="Max queued notifications per user",
    )

    # Broadcast settings
    broadcast_buffer_size: int = Field(
        default=100,
        ge=10,
        le=1000,
        description="Broadcast message buffer size",
    )

    # Presence settings
    presence_timeout: int = Field(
        default=300,
        ge=60,
        le=3600,
        description="Presence timeout (seconds)",
    )

    presence_update_interval: int = Field(
        default=30,
        ge=10,
        le=300,
        description="Presence update interval (seconds)",
    )


class ServerConfig(BaseModel):
    """
    Complete server configuration combining all settings.

    Example:
        >>> config = ServerConfig(
        ...     server=WSServerConfig(host="0.0.0.0", port=8765),
        ...     handlers=HandlerConfig(enable_notifications=True),
        ... )
    """

    server: WSServerConfig = Field(
        default_factory=WSServerConfig,
        description="WebSocket server settings",
    )

    handlers: HandlerConfig = Field(
        default_factory=HandlerConfig,
        description="Handler settings",
    )

    def model_dump_safe(self) -> dict:
        """
        Dump config excluding sensitive data.

        Returns:
            Config dict without secrets
        """
        data = self.model_dump()

        # Mask sensitive fields
        if "server" in data and "jwt_secret" in data["server"]:
            if data["server"]["jwt_secret"]:
                data["server"]["jwt_secret"] = "***MASKED***"

        return data


__all__ = [
    "LogLevel",
    "AuthMode",
    "WSServerConfig",
    "HandlerConfig",
    "ServerConfig",
]
