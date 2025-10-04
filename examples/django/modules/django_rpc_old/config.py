"""
WebSocket RPC Configuration for Django-CFG.

Pydantic 2 configuration model for WebSocket RPC integration.
Follows django-cfg patterns for modular configuration.

File size: ~250 lines
"""

from pydantic import Field, field_validator
import logging
import os

from django_cfg.models.base import BaseCfgAutoModule

logger = logging.getLogger(__name__)


class WebSocketRPCConfig(BaseCfgAutoModule):
    """
    WebSocket RPC configuration module.

    Configures Redis-based RPC communication between Django and
    external WebSocket servers.

    Example:
        >>> from django_cfg import DjangoConfig
        >>> from django_cfg.modules.django_rpc import WebSocketRPCConfig
        >>>
        >>> config = DjangoConfig(
        ...     websocket_rpc=WebSocketRPCConfig(
        ...         enabled=True,
        ...         redis_url="redis://localhost:6379/2",
        ...         rpc_timeout=30
        ...     )
        ... )
    """

    # Module metadata
    module_name: str = Field(
        default="websocket_rpc",
        frozen=True,
        description="Module name for django-cfg integration",
    )

    enabled: bool = Field(
        default=False,
        description="Enable WebSocket RPC layer",
    )

    # Redis configuration
    redis_url: str = Field(
        default="redis://localhost:6379/2",
        description="Redis URL for WebSocket RPC (dedicated database recommended)",
        examples=[
            "redis://localhost:6379/2",
            "redis://:password@localhost:6379/2",
            "redis://redis-server:6379/2",
        ],
    )

    redis_max_connections: int = Field(
        default=50,
        ge=10,
        le=500,
        description="Maximum Redis connection pool size",
    )

    # RPC settings
    rpc_timeout: int = Field(
        default=30,
        ge=5,
        le=300,
        description="Default RPC call timeout (seconds)",
    )

    request_stream: str = Field(
        default="stream:requests",
        min_length=1,
        max_length=100,
        description="Redis Stream name for RPC requests",
    )

    consumer_group: str = Field(
        default="rpc_group",
        min_length=1,
        max_length=100,
        description="Redis Streams consumer group name",
    )

    stream_maxlen: int = Field(
        default=10000,
        ge=1000,
        le=100000,
        description="Maximum stream length (XADD MAXLEN)",
    )

    # Response settings
    response_key_prefix: str = Field(
        default="list:response:",
        min_length=1,
        max_length=50,
        description="Prefix for response list keys",
    )

    response_key_ttl: int = Field(
        default=60,
        ge=10,
        le=3600,
        description="Response key TTL (seconds) for auto-cleanup",
    )

    # Bridge listener settings (for receiving messages from WS)
    enable_bridge: bool = Field(
        default=False,
        description="Enable Redis bridge listener for incoming RPC",
    )

    bridge_consumer_name: str = Field(
        default="django_bridge",
        min_length=1,
        max_length=100,
        description="Consumer name for bridge listener",
    )

    bridge_stream: str = Field(
        default="stream:django:requests",
        min_length=1,
        max_length=100,
        description="Redis Stream for incoming requests to Django",
    )

    # WebSocket server settings (for client-side reference)
    websocket_url: str = Field(
        default="ws://localhost:8765",
        description="WebSocket server URL (for documentation/testing)",
        examples=["ws://localhost:8765", "wss://ws.example.com"],
    )

    # Performance settings
    enable_connection_pooling: bool = Field(
        default=True,
        description="Enable Redis connection pooling",
    )

    socket_keepalive: bool = Field(
        default=True,
        description="Enable TCP keepalive for Redis connections",
    )

    socket_keepalive_options: dict[str, int] = Field(
        default={
            "socket_keepalive": 1,
            "socket_keepalive_idle": 30,
            "socket_keepalive_intvl": 10,
            "socket_keepalive_cnt": 3,
        },
        description="TCP keepalive options for Redis sockets",
    )

    # Logging settings
    log_rpc_calls: bool = Field(
        default=False,
        description="Log all RPC calls (verbose, use for debugging)",
    )

    log_level: str = Field(
        default="INFO",
        pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="Log level for RPC module",
    )

    @field_validator("redis_url")
    @classmethod
    def validate_redis_url(cls, v: str) -> str:
        """
        Validate Redis URL format.

        Args:
            v: Redis URL to validate

        Returns:
            Validated Redis URL

        Raises:
            ValueError: If URL format is invalid
        """
        if not v.startswith("redis://") and not v.startswith("rediss://"):
            raise ValueError(
                "redis_url must start with 'redis://' or 'rediss://' "
                f"(got: {v})"
            )

        return v

    @field_validator("websocket_url")
    @classmethod
    def validate_websocket_url(cls, v: str) -> str:
        """
        Validate WebSocket URL format.

        Args:
            v: WebSocket URL to validate

        Returns:
            Validated WebSocket URL

        Raises:
            ValueError: If URL format is invalid
        """
        if not v.startswith("ws://") and not v.startswith("wss://"):
            raise ValueError(
                "websocket_url must start with 'ws://' or 'wss://' "
                f"(got: {v})"
            )

        return v

    def to_django_settings(self) -> dict:
        """
        Generate Django settings dictionary.

        Returns:
            Dictionary with WEBSOCKET_RPC settings

        Example:
            >>> config = WebSocketRPCConfig(enabled=True)
            >>> settings_dict = config.to_django_settings()
            >>> print(settings_dict["WEBSOCKET_RPC"]["REDIS_URL"])
        """
        if not self.enabled:
            return {}

        return {
            "WEBSOCKET_RPC": {
                "ENABLED": self.enabled,
                "REDIS_URL": self.redis_url,
                "REDIS_MAX_CONNECTIONS": self.redis_max_connections,
                "RPC_TIMEOUT": self.rpc_timeout,
                "REQUEST_STREAM": self.request_stream,
                "CONSUMER_GROUP": self.consumer_group,
                "STREAM_MAXLEN": self.stream_maxlen,
                "RESPONSE_KEY_PREFIX": self.response_key_prefix,
                "RESPONSE_KEY_TTL": self.response_key_ttl,
                "ENABLE_BRIDGE": self.enable_bridge,
                "BRIDGE_CONSUMER_NAME": self.bridge_consumer_name,
                "BRIDGE_STREAM": self.bridge_stream,
                "WEBSOCKET_URL": self.websocket_url,
                "LOG_RPC_CALLS": self.log_rpc_calls,
                "LOG_LEVEL": self.log_level,
            }
        }

    def get_redis_config(self) -> dict:
        """
        Get Redis connection configuration.

        Returns:
            Dictionary with Redis connection options

        Example:
            >>> config = WebSocketRPCConfig()
            >>> redis_config = config.get_redis_config()
            >>> redis_client = redis.Redis.from_url(**redis_config)
        """
        config = {
            "url": self.redis_url,
            "max_connections": self.redis_max_connections,
            "decode_responses": False,  # We handle JSON ourselves
        }

        if self.socket_keepalive:
            config["socket_keepalive"] = True
            config["socket_keepalive_options"] = self.socket_keepalive_options

        return config


__all__ = ["WebSocketRPCConfig"]
