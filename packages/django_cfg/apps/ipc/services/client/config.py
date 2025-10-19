"""
Django-CFG RPC Client Configuration.

Pydantic 2 configuration model for RPC client integration.
Follows django-cfg patterns for modular configuration.
"""

from pydantic import BaseModel, Field, field_validator


class DjangoCfgRPCConfig(BaseModel):
    """
    Django-CFG RPC Client configuration module.

    Configures Redis-based RPC communication between Django and
    django-cfg-rpc WebSocket servers.

    Example:
        >>> from django_cfg import DjangoConfig
        >>> from django_cfg.modules.django_ipc_client import DjangoCfgRPCConfig
        >>>
        >>> config = DjangoConfig(
        ...     django_ipc=DjangoCfgRPCConfig(
        ...         enabled=True,
        ...         redis_url="redis://localhost:6379/2",
        ...         rpc_timeout=30
        ...     )
        ... )
    """

    # Module metadata
    module_name: str = Field(
        default="django_ipc_client",
        frozen=True,
        description="Module name for django-cfg integration",
    )

    enabled: bool = Field(
        default=False,
        description="Enable Django-CFG RPC client",
    )

    # Redis configuration
    redis_url: str = Field(
        default="redis://localhost:6379/2",
        description="Redis URL for RPC communication (dedicated database recommended)",
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
        description="Redis Streams consumer group name (on server side)",
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

    # Performance settings
    enable_connection_pooling: bool = Field(
        default=True,
        description="Enable Redis connection pooling",
    )

    socket_keepalive: bool = Field(
        default=True,
        description="Enable TCP keepalive for Redis connections",
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

        Allows environment variable templates like ${VAR:-default}.

        Args:
            v: Redis URL to validate

        Returns:
            Validated Redis URL

        Raises:
            ValueError: If URL format is invalid
        """
        # Skip validation for environment variable templates
        if v.startswith("${") and "}" in v:
            return v

        # Validate actual URLs
        if not v.startswith("redis://") and not v.startswith("rediss://"):
            raise ValueError(
                "redis_url must start with 'redis://' or 'rediss://' "
                f"(got: {v})"
            )

        return v

    def to_django_settings(self) -> dict:
        """
        Generate Django settings dictionary.

        Returns:
            Dictionary with DJANGO_CFG_RPC settings

        Example:
            >>> config = DjangoCfgRPCConfig(enabled=True)
            >>> settings_dict = config.to_django_settings()
            >>> print(settings_dict["DJANGO_CFG_RPC"]["REDIS_URL"])
        """
        if not self.enabled:
            return {}

        return {
            "DJANGO_CFG_RPC": {
                "ENABLED": self.enabled,
                "REDIS_URL": self.redis_url,
                "REDIS_MAX_CONNECTIONS": self.redis_max_connections,
                "RPC_TIMEOUT": self.rpc_timeout,
                "REQUEST_STREAM": self.request_stream,
                "CONSUMER_GROUP": self.consumer_group,
                "STREAM_MAXLEN": self.stream_maxlen,
                "RESPONSE_KEY_PREFIX": self.response_key_prefix,
                "RESPONSE_KEY_TTL": self.response_key_ttl,
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
            >>> config = DjangoCfgRPCConfig()
            >>> redis_config = config.get_redis_config()
            >>> import redis
            >>> redis_client = redis.Redis.from_url(**redis_config)
        """
        config = {
            "url": self.redis_url,
            "max_connections": self.redis_max_connections,
            "decode_responses": False,  # We handle JSON ourselves
        }

        if self.socket_keepalive:
            config["socket_keepalive"] = True

        return config


__all__ = ["DjangoCfgRPCConfig"]
