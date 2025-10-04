"""
RPC Configuration Models

Pydantic models for environment-aware RPC server configuration.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator
from .environment import Environment, detect_environment


class RPCEndpointConfig(BaseModel):
    """
    Configuration for a single RPC endpoint (environment).

    Contains WebSocket URL, Redis URL, and optional metadata
    for one specific environment.

    Example:
        >>> config = RPCEndpointConfig(
        ...     websocket_url="ws://localhost:8001/ws",
        ...     redis_url="redis://localhost:6379/2",
        ...     description="Local development environment",
        ... )
    """

    websocket_url: str = Field(
        ...,
        description="WebSocket URL for RPC connection (e.g., 'ws://localhost:8001/ws')",
        min_length=1,
    )

    redis_url: str = Field(
        ...,
        description="Redis connection URL (e.g., 'redis://localhost:6379/2')",
        min_length=1,
    )

    http_url: Optional[str] = Field(
        None,
        description="Optional HTTP API URL for REST fallback",
    )

    description: Optional[str] = Field(
        None,
        description="Human-readable description of this environment",
    )

    @field_validator("websocket_url")
    @classmethod
    def validate_websocket_url(cls, v: str) -> str:
        """Validate WebSocket URL format."""
        if not v.startswith(("ws://", "wss://")):
            raise ValueError(
                "WebSocket URL must start with 'ws://' or 'wss://'. "
                f"Got: {v}"
            )
        return v

    @field_validator("redis_url")
    @classmethod
    def validate_redis_url(cls, v: str) -> str:
        """Validate Redis URL format."""
        if not v.startswith(("redis://", "rediss://")):
            raise ValueError(
                "Redis URL must start with 'redis://' or 'rediss://'. "
                f"Got: {v}"
            )
        return v

    @field_validator("http_url")
    @classmethod
    def validate_http_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate HTTP URL format if provided."""
        if v and not v.startswith(("http://", "https://")):
            raise ValueError(
                "HTTP URL must start with 'http://' or 'https://'. "
                f"Got: {v}"
            )
        return v


class RPCServerConfig(BaseModel):
    """
    Multi-environment RPC server configuration.

    Manages WebSocket and Redis URLs for different environments
    (development/production/staging/testing) with automatic
    environment detection.

    Example:
        >>> config = RPCServerConfig(
        ...     development=RPCEndpointConfig(
        ...         websocket_url="ws://localhost:8001/ws",
        ...         redis_url="redis://localhost:6379/2",
        ...     ),
        ...     production=RPCEndpointConfig(
        ...         websocket_url="wss://api.example.com/ws",
        ...         redis_url="redis://prod-redis.example.com:6379/0",
        ...     ),
        ... )
        >>>
        >>> # Get endpoint for current environment
        >>> endpoint = config.get_current_endpoint()
        >>> print(endpoint.websocket_url)
        'ws://localhost:8001/ws'
    """

    development: RPCEndpointConfig = Field(
        ...,
        description="Development environment configuration (required)",
    )

    production: RPCEndpointConfig = Field(
        ...,
        description="Production environment configuration (required)",
    )

    staging: Optional[RPCEndpointConfig] = Field(
        None,
        description="Staging environment configuration (optional)",
    )

    testing: Optional[RPCEndpointConfig] = Field(
        None,
        description="Testing environment configuration (optional)",
    )

    default_environment: Environment = Field(
        default="development",
        description="Default environment if detection fails",
    )

    def get_endpoint(self, environment: Environment) -> RPCEndpointConfig:
        """
        Get endpoint configuration for specific environment.

        Args:
            environment: Environment name (development/production/staging/testing)

        Returns:
            RPCEndpointConfig for the specified environment

        Raises:
            ValueError: If environment is not configured

        Example:
            >>> config = RPCServerConfig(...)
            >>> dev_endpoint = config.get_endpoint("development")
            >>> print(dev_endpoint.websocket_url)
            'ws://localhost:8001/ws'
        """
        env_map = {
            "development": self.development,
            "production": self.production,
            "staging": self.staging,
            "testing": self.testing,
        }

        endpoint = env_map.get(environment)

        if endpoint is None:
            # Get list of configured environments
            configured = [
                env for env, cfg in env_map.items() if cfg is not None
            ]

            raise ValueError(
                f"No configuration found for environment '{environment}'. "
                f"Configured environments: {', '.join(configured)}. "
                f"Please add '{environment}' configuration to RPCServerConfig."
            )

        return endpoint

    def get_current_endpoint(self) -> RPCEndpointConfig:
        """
        Get endpoint configuration for current detected environment.

        Automatically detects environment from DJANGO_ENV, ENV, or DEBUG
        environment variables and returns the appropriate configuration.

        Returns:
            RPCEndpointConfig for current environment

        Example:
            >>> import os
            >>> os.environ['DJANGO_ENV'] = 'production'
            >>>
            >>> config = RPCServerConfig(...)
            >>> endpoint = config.get_current_endpoint()
            >>> print(endpoint.websocket_url)
            'wss://api.example.com/ws'
        """
        try:
            env = detect_environment()
            return self.get_endpoint(env)
        except ValueError:
            # Fallback to default environment if detected env not configured
            return self.get_endpoint(self.default_environment)

    def get_websocket_url(self, environment: Optional[Environment] = None) -> str:
        """
        Get WebSocket URL for environment (convenience method).

        Args:
            environment: Environment name (auto-detect if None)

        Returns:
            WebSocket URL string

        Example:
            >>> config = RPCServerConfig(...)
            >>> url = config.get_websocket_url("production")
            >>> print(url)
            'wss://api.example.com/ws'
        """
        if environment is None:
            endpoint = self.get_current_endpoint()
        else:
            endpoint = self.get_endpoint(environment)

        return endpoint.websocket_url

    def get_redis_url(self, environment: Optional[Environment] = None) -> str:
        """
        Get Redis URL for environment (convenience method).

        Args:
            environment: Environment name (auto-detect if None)

        Returns:
            Redis URL string

        Example:
            >>> config = RPCServerConfig(...)
            >>> url = config.get_redis_url("production")
            >>> print(url)
            'redis://prod-redis.example.com:6379/0'
        """
        if environment is None:
            endpoint = self.get_current_endpoint()
        else:
            endpoint = self.get_endpoint(environment)

        return endpoint.redis_url

    def list_environments(self) -> list[str]:
        """
        Get list of configured environments.

        Returns:
            List of environment names

        Example:
            >>> config = RPCServerConfig(
            ...     development=...,
            ...     production=...,
            ...     staging=...,
            ... )
            >>> config.list_environments()
            ['development', 'production', 'staging']
        """
        envs = []

        if self.development:
            envs.append("development")
        if self.production:
            envs.append("production")
        if self.staging:
            envs.append("staging")
        if self.testing:
            envs.append("testing")

        return envs


__all__ = [
    "RPCEndpointConfig",
    "RPCServerConfig",
]
