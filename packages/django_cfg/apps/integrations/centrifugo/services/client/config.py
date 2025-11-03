"""
Centrifugo Client Configuration.

Pydantic 2 configuration model for Centrifugo integration.
Follows django-cfg patterns for modular configuration.
"""

from pydantic import BaseModel, Field, field_validator


class DjangoCfgCentrifugoConfig(BaseModel):
    """
    Django-CFG Centrifugo Client configuration module.

    Configures Centrifugo pub/sub communication between Django and
    Centrifugo WebSocket server via Python Wrapper.

    Example:
        >>> from django_cfg import DjangoConfig
        >>> from django_cfg.apps.integrations.centrifugo import DjangoCfgCentrifugoConfig
        >>>
        >>> config = DjangoConfig(
        ...     centrifugo=DjangoCfgCentrifugoConfig(
        ...         enabled=True,
        ...         wrapper_url="http://localhost:8080",
        ...         default_timeout=30
        ...     )
        ... )
    """

    # Module metadata
    module_name: str = Field(
        default="centrifugo",
        frozen=True,
        description="Module name for django-cfg integration",
    )

    enabled: bool = Field(
        default=False,
        description="Enable Centrifugo integration",
    )

    # Wrapper configuration
    wrapper_url: str = Field(
        default="http://localhost:8080",
        description="Python Wrapper HTTP API URL",
        examples=[
            "http://localhost:8080",
            "http://centrifugo-wrapper:8080",
            "https://wrapper.example.com",
        ],
    )

    wrapper_api_key: str | None = Field(
        default=None,
        description="Optional API key for wrapper authentication",
    )

    # Centrifugo settings
    centrifugo_url: str = Field(
        default="ws://localhost:8002/connection/websocket",
        description="Centrifugo WebSocket URL for browser clients",
        examples=[
            "ws://localhost:8002/connection/websocket",
            "wss://centrifugo.example.com/connection/websocket",
        ],
    )

    centrifugo_api_url: str = Field(
        default="http://localhost:8002/api",
        description="Centrifugo HTTP API URL for server-to-server calls",
        examples=[
            "http://localhost:8002/api",
            "https://centrifugo.example.com/api",
        ],
    )

    centrifugo_api_key: str | None = Field(
        default=None,
        description="Centrifugo API key for server-to-server authentication",
    )

    centrifugo_token_hmac_secret: str | None = Field(
        default=None,
        description="HMAC secret for JWT token generation (if None, uses Django SECRET_KEY)",
    )

    # Timeout settings
    default_timeout: int = Field(
        default=30,
        ge=5,
        le=300,
        description="Default publish timeout (seconds)",
    )

    ack_timeout: int = Field(
        default=10,
        ge=1,
        le=60,
        description="Default ACK timeout for delivery confirmation (seconds)",
    )

    http_timeout: int = Field(
        default=35,
        ge=5,
        le=300,
        description="HTTP request timeout to wrapper (seconds)",
    )

    # Retry settings
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retry attempts for failed publishes",
    )

    retry_delay: float = Field(
        default=1.0,
        ge=0.1,
        le=10.0,
        description="Delay between retries (seconds)",
    )

    # SSL settings
    verify_ssl: bool = Field(
        default=False,
        description="Verify SSL certificates for HTTPS connections (default: False for self-signed certs)",
    )

    # Logging settings
    log_all_calls: bool = Field(
        default=False,
        description="Log all publish calls to database (verbose)",
    )

    log_only_with_ack: bool = Field(
        default=True,
        description="Only log calls that wait for ACK",
    )

    log_level: str = Field(
        default="INFO",
        pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="Log level for Centrifugo module",
    )

    @field_validator("wrapper_url", "centrifugo_url")
    @classmethod
    def validate_urls(cls, v: str) -> str:
        """
        Validate URL formats.

        Allows environment variable templates like ${VAR:-default}.

        Args:
            v: URL to validate

        Returns:
            Validated URL

        Raises:
            ValueError: If URL format is invalid
        """
        # Skip validation for environment variable templates
        if v.startswith("${") and "}" in v:
            return v

        # Validate actual URLs
        if not any(v.startswith(proto) for proto in ["http://", "https://", "ws://", "wss://"]):
            raise ValueError(
                f"URL must start with http://, https://, ws://, or wss:// (got: {v})"
            )

        return v

    def to_django_settings(self) -> dict:
        """
        Generate Django settings dictionary.

        Returns:
            Dictionary with DJANGO_CFG_CENTRIFUGO settings

        Example:
            >>> config = DjangoCfgCentrifugoConfig(enabled=True)
            >>> settings_dict = config.to_django_settings()
            >>> print(settings_dict["DJANGO_CFG_CENTRIFUGO"]["WRAPPER_URL"])
        """
        if not self.enabled:
            return {}

        return {
            "DJANGO_CFG_CENTRIFUGO": {
                "ENABLED": self.enabled,
                "WRAPPER_URL": self.wrapper_url,
                "WRAPPER_API_KEY": self.wrapper_api_key,
                "CENTRIFUGO_URL": self.centrifugo_url,
                "CENTRIFUGO_API_URL": self.centrifugo_api_url,
                "CENTRIFUGO_API_KEY": self.centrifugo_api_key,
                "CENTRIFUGO_TOKEN_HMAC_SECRET": self.centrifugo_token_hmac_secret,
                "DEFAULT_TIMEOUT": self.default_timeout,
                "ACK_TIMEOUT": self.ack_timeout,
                "HTTP_TIMEOUT": self.http_timeout,
                "MAX_RETRIES": self.max_retries,
                "RETRY_DELAY": self.retry_delay,
                "VERIFY_SSL": self.verify_ssl,
                "LOG_ALL_CALLS": self.log_all_calls,
                "LOG_ONLY_WITH_ACK": self.log_only_with_ack,
                "LOG_LEVEL": self.log_level,
            }
        }

    def get_client_config(self) -> dict:
        """
        Get client configuration dictionary.

        Returns:
            Dictionary with client connection options

        Example:
            >>> config = DjangoCfgCentrifugoConfig()
            >>> client_config = config.get_client_config()
        """
        return {
            "wrapper_url": self.wrapper_url,
            "wrapper_api_key": self.wrapper_api_key,
            "default_timeout": self.default_timeout,
            "ack_timeout": self.ack_timeout,
            "http_timeout": self.http_timeout,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "verify_ssl": self.verify_ssl,
        }


__all__ = ["DjangoCfgCentrifugoConfig"]
