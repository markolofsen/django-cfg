"""
Environment Configuration Loader for Django CFG Sample

Modern approach using pydantic-settings BaseSettings.
Priority: ENV > .env.secrets (if exists) > .env.prod (if prod) > .env > Defaults

Loading strategy:
1. Environment variables with __ notation (e.g., EMAIL__HOST, DATABASE__URL)
2. Load .env.secrets file if exists (contains actual secrets, never committed)
3. Load .env.prod file if IS_PROD=true (production overrides)
4. Load .env file (base/dev configuration)
5. Use defaults from field definitions

File structure:
    - .env          - Base configuration (non-sensitive defaults)
    - .env.prod     - Production overrides (only prod-specific values)
    - .env.secrets  - Secrets (API keys, passwords) - NEVER commit!

Dependencies:
    - pydantic-settings
    - python-dotenv
"""

import os
from pathlib import Path
from typing import Optional, Tuple
from pydantic import Field, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# ─────────────────────────────────────────────────────────────────────────────
# Environment file detection
# ─────────────────────────────────────────────────────────────────────────────
ENV_DIR = Path(__file__).parent


def get_env_files() -> Tuple[str, ...]:
    """
    Determine which .env files to load based on environment.

    Priority (later files override earlier):
    1. .env - always loaded (base/dev config)
    2. .env.prod - loaded only if IS_PROD=true
    3. .env.secrets - loaded if exists (contains actual secrets)

    Returns tuple of file paths for pydantic-settings.
    """
    base_env = ENV_DIR / ".env"
    prod_env = ENV_DIR / ".env.prod"
    secrets_env = ENV_DIR / ".env.secrets"

    # Check if production mode (from ENV variable)
    is_prod = os.getenv("IS_PROD", "false").lower() in ("true", "1", "yes")

    files = []

    # Base .env file (always load if exists)
    if base_env.exists():
        files.append(str(base_env))

    # Production overrides (only if IS_PROD=true and file exists)
    if is_prod and prod_env.exists():
        files.append(str(prod_env))

    # Secrets file (highest priority, loaded last to override)
    if secrets_env.exists():
        files.append(str(secrets_env))

    return tuple(files) if files else (str(base_env),)


class DatabaseConfig(BaseSettings):
    """Database connection configuration."""

    url: str = Field(
        default="sqlite:///db/default.sqlite3",
        description="Database connection URL"
    )

    model_config = SettingsConfigDict(
        env_prefix="DATABASE__",
        env_nested_delimiter="__",
    )


class EmailConfig(BaseSettings):
    """Email configuration."""

    backend: str = Field(default="console", description="Email backend (smtp/console)")
    host: str = Field(default="localhost", description="SMTP server hostname")
    port: int = Field(default=587, description="SMTP server port")
    username: Optional[str] = Field(default=None, description="SMTP username")
    password: Optional[str] = Field(default=None, description="SMTP password")
    use_tls: bool = Field(default=True, description="Use TLS encryption")
    use_ssl: bool = Field(default=False, description="Use SSL encryption")
    ssl_verify: bool = Field(default=False, description="Verify SSL certificates")
    default_from: str = Field(default="noreply@sample.local", description="Default from email")

    model_config = SettingsConfigDict(
        env_prefix="EMAIL__",
        env_nested_delimiter="__",
    )


class TelegramConfig(BaseSettings):
    """Telegram bot configuration."""

    bot_token: str = Field(default="", description="Telegram bot token")
    chat_id: int = Field(default=0, description="Telegram chat ID")

    model_config = SettingsConfigDict(
        env_prefix="TELEGRAM__",
        env_nested_delimiter="__",
    )


class ApiKeysConfig(BaseSettings):
    """API keys configuration."""

    openrouter: str = Field(default="", description="OpenRouter API key")
    openai: str = Field(default="", description="OpenAI API key")

    model_config = SettingsConfigDict(
        env_prefix="API_KEYS__",
        env_nested_delimiter="__",
    )


class PaymentsApiKeysConfig(BaseSettings):
    """Payments API keys configuration."""

    nowpayments_api_key: str = Field(default="", description="NOWPayments API key")
    nowpayments_ipn_secret: str = Field(default="", description="NOWPayments IPN secret")
    nowpayments_sandbox_mode: bool = Field(default=True, description="Use sandbox mode")

    model_config = SettingsConfigDict(
        env_prefix="PAYMENTS_API_KEYS__",
        env_nested_delimiter="__",
    )


class AppConfig(BaseSettings):
    """Application configuration."""

    name: str = Field(default="Django CFG", description="Application name")
    logo_url: str = Field(default="https://djangocfg.com/img/logo.png", description="Application logo URL")
    domain: str = Field(default="localhost", description="Application domain")
    api_url: str = Field(default="http://localhost:8000", description="API base URL")
    site_url: str = Field(default="http://localhost:3000", description="Site base URL")

    model_config = SettingsConfigDict(
        env_prefix="APP__",
        env_nested_delimiter="__",
    )


class GitHubOAuthEnvConfig(BaseSettings):
    """GitHub OAuth configuration."""

    client_id: str = Field(default="", description="GitHub OAuth App Client ID")
    client_secret: str = Field(default="", description="GitHub OAuth App Client Secret")

    model_config = SettingsConfigDict(
        env_prefix="GITHUB_OAUTH__",
        env_nested_delimiter="__",
    )


class CentrifugoConfig(BaseSettings):
    """Centrifugo WebSocket pub/sub configuration."""

    enabled: bool = Field(default=True, description="Enable Centrifugo client")

    # Wrapper configuration (for Django backend publishing)
    wrapper_url: str = Field(default="http://localhost:8000/cfg/centrifugo", description="Centrifugo wrapper URL")
    wrapper_api_key: Optional[str] = Field(default=None, description="Centrifugo wrapper API key")

    # Centrifugo server configuration (for browser WebSocket connections)
    centrifugo_url: str = Field(
        default="ws://localhost:8120/connection/websocket",
        description="Centrifugo WebSocket URL for browser clients"
    )
    centrifugo_api_url: str = Field(
        default="http://localhost:8120/api",
        description="Centrifugo HTTP API URL"
    )
    centrifugo_api_key: str = Field(
        default="centrifugo-api-key-change-in-production-min-32-chars",
        description="Centrifugo API key for server-to-server calls"
    )
    # IMPORTANT: Must match CENTRIFUGO_TOKEN_HMAC_SECRET (Centrifugo server) for JWT token validation
    centrifugo_token_hmac_secret: str = Field(
        default="django-secret-key-change-in-production-at-least-32-chars",
        description="HMAC secret for JWT token generation (client auth)"
    )

    # Timeouts and behavior
    default_ack_timeout: int = Field(default=10, description="Default ACK timeout in seconds")
    log_publishes: bool = Field(default=True, description="Log all publish operations")
    log_level: str = Field(default="INFO", description="Logging level")

    # Database logging configuration
    log_all_calls: bool = Field(default=True, description="Log all publish calls to database")
    log_only_with_ack: bool = Field(default=False, description="Only log calls that wait for ACK")

    model_config = SettingsConfigDict(
        env_prefix="CENTRIFUGO__",
        env_nested_delimiter="__",
    )


class EnvironmentMode(BaseSettings):
    """
    Environment mode detection via ENV variables.

    Set via: IS_TEST=true, IS_PROD=true, or IS_DEV=true
    If nothing is set, defaults to development mode.
    """

    is_test: bool = Field(default=False, description="Test environment")
    is_dev: bool = Field(default=False, description="Development environment")
    is_prod: bool = Field(default=False, description="Production environment")

    @model_validator(mode="after")
    def set_default_env(self):
        """Default to development if no environment is set."""
        if not any([self.is_test, self.is_dev, self.is_prod]):
            self.is_dev = True
        return self

    @computed_field
    @property
    def env_mode(self) -> str:
        """Get current environment mode as string."""
        if self.is_test:
            return "test"
        elif self.is_prod:
            return "production"
        return "development"

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
    )


class EnvironmentConfig(BaseSettings):
    """
    Complete environment configuration with automatic ENV and .env loading.

    Priority: ENV > .env > Defaults
    - ENV variables use __ notation: EMAIL__HOST, API_KEYS__OPENAI, DATABASE__URL
    - .env file loaded automatically
    - Defaults defined in field definitions
    """

    # Core Django settings
    # IMPORTANT: Must match CENTRIFUGO_TOKEN_HMAC_SECRET for JWT token generation
    secret_key: str = Field(
        default="django-secret-key-change-in-production-at-least-32-chars",
        description="Django secret key (also used for Centrifugo JWT tokens)"
    )
    debug: bool = Field(default=True, description="Enable debug mode")

    # Admin Configuration
    admin_emails: Optional[list[str]] = Field(default=None, description="Admin email addresses")

    # Configuration sections (nested configs)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    email: EmailConfig = Field(default_factory=EmailConfig)
    telegram: TelegramConfig = Field(default_factory=TelegramConfig)
    api_keys: ApiKeysConfig = Field(default_factory=ApiKeysConfig)
    payments_api_keys: PaymentsApiKeysConfig = Field(default_factory=PaymentsApiKeysConfig)
    app: AppConfig = Field(default_factory=AppConfig)
    env: EnvironmentMode = Field(default_factory=EnvironmentMode)
    centrifugo: CentrifugoConfig = Field(default_factory=CentrifugoConfig)
    github_oauth: GitHubOAuthEnvConfig = Field(default_factory=GitHubOAuthEnvConfig)

    # gRPC Configuration
    grpc_url: Optional[str] = Field(
        default=None,
        description="Public gRPC URL for clients (e.g., grpc.djangocfg.com:443). If None, auto-generated from api_url",
    )

    # Cache Configuration
    # IMPORTANT: Redis URL for django-cfg CacheConfig
    # If not set, django-cfg will fallback to FileBasedCache in production
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for cache backend (required for production)",
    )

    # Security domains
    security_domains: Optional[list[str]] = Field(
        default=[
            "demo.djangocfg.com",
            "djangocfg.com",
            "api.djangocfg.com",
            "localhost",
            "127.0.0.1",
            # Docker exposed ports for CSRF (CORS uses regex for all ports)
            "localhost:3777",  # Next.js Admin App
            "localhost:7301",  # Django API
            "localhost:7310",  # Frontend Demo
            "localhost:7311",  # Frontend Web
            "localhost:7320",  # WebSocket
            "127.0.0.1:7301",
            "127.0.0.1:7310",
            "127.0.0.1:7311",
            "127.0.0.1:7320",
        ],
        description="Allowed security domains"
    )

    model_config = SettingsConfigDict(
        env_file=get_env_files(),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )


# Global environment configuration instance
# Automatically loads from:
# 1. Environment variables (highest priority)
# 2. .env.secrets file (if exists - contains actual secrets)
# 3. .env.prod file (if IS_PROD=true and file exists)
# 4. .env file (base/dev configuration)
# 5. Default values defined above
env = EnvironmentConfig()
