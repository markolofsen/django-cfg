"""
Environment Configuration Loader for Django CFG Sample

Simple approach: Load YAML, then override with environment variables.
Priority: ENV > YAML > Defaults
"""

import os
import sys
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field, computed_field
from pydantic_yaml import parse_yaml_file_as

# Environment detection
IS_DEV = os.environ.get("IS_DEV", "").lower() in ("true", "1", "yes")
IS_PROD = os.environ.get("IS_PROD", "").lower() in ("true", "1", "yes")
IS_TEST = os.environ.get("IS_TEST", "").lower() in ("true", "1", "yes") or "test" in sys.argv
DEBUG = os.environ.get("DEBUG", "").lower() in ("true", "1", "yes")

# Default to development if not explicitly set
if not any([IS_DEV, IS_PROD, IS_TEST]):
    IS_DEV = True


class DatabaseConfig(BaseModel):
    """Database connection configuration."""

    url: str = "sqlite:///db/default.sqlite3"
    url_blog: str = "sqlite:///db/blog.sqlite3"
    url_shop: str = "sqlite:///db/shop.sqlite3"


class EmailConfig(BaseModel):
    """Email configuration."""

    backend: str = "console"
    host: str = "localhost"
    port: int = 587
    username: Optional[str] = None
    password: Optional[str] = None
    use_tls: bool = True
    use_ssl: bool = False
    default_from: str = "noreply@sample.local"


class TelegramConfig(BaseModel):
    """Telegram bot configuration."""

    bot_token: str = ""
    chat_id: int = 0


class ApiKeysConfig(BaseModel):
    """API keys configuration."""

    openrouter: str = ""
    openai: str = ""


class PaymentsApiKeysConfig(BaseModel):
    """Payments API keys configuration."""

    nowpayments_api_key: str = ""
    nowpayments_ipn_secret: str = ""
    nowpayments_sandbox_mode: bool = True


class AppConfig(BaseModel):
    """Application configuration."""

    name: str = "Django CFG"
    logo_url: str = ""
    domain: str = "localhost"
    api_url: str = "http://localhost:8000"
    site_url: str = "http://localhost:3000"
    dashboard_url: str = "http://localhost:3000/dashboard"
    ticket_url: str = "http://localhost:3000/support/ticket/{uuid}"
    otp_url: str = "http://localhost:3000/auth/otp/{code}"


class RPCConfig(BaseModel):
    """RPC client configuration."""

    enabled: bool = False
    redis_url: str = "redis://localhost:6379/2"
    redis_max_connections: int = 50
    rpc_timeout: int = 30
    request_stream: str = "stream:rpc_requests"
    consumer_group: str = "django_rpc_group"
    stream_maxlen: int = 10000
    response_key_prefix: str = "list:response:"
    response_key_ttl: int = 60
    log_rpc_calls: bool = False
    log_level: str = "INFO"


class EnvironmentMode(BaseModel):
    """Environment mode."""

    is_test: bool = IS_TEST
    is_dev: bool = IS_DEV
    is_prod: bool = IS_PROD

    @computed_field
    @property
    def env_mode(self) -> str:
        """Environment mode."""
        if self.is_test:
            return "test"
        elif self.is_dev:
            return "development"
        elif self.is_prod:
            return "production"
        else:
            return "development"


class EnvironmentConfig(BaseModel):
    """Complete environment configuration."""

    # Core Django settings
    secret_key: str = "django-cfg-sample-secret-key-change-in-production"
    debug: bool = True

    # Admin Configuration
    admin_emails: Optional[list[str]] = None

    # Configuration sections
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    email: EmailConfig = Field(default_factory=EmailConfig)
    telegram: TelegramConfig = Field(default_factory=TelegramConfig)
    api_keys: ApiKeysConfig = Field(default_factory=ApiKeysConfig)
    payments_api_keys: PaymentsApiKeysConfig = Field(default_factory=PaymentsApiKeysConfig)
    app: AppConfig = Field(default_factory=AppConfig)
    env: EnvironmentMode = Field(default_factory=EnvironmentMode)
    rpc: RPCConfig = Field(default_factory=RPCConfig)
    
    # Cache
    redis_url: Optional[str] = None

    # Security (default ports for both projects: StockAPIs=3100, Django-CFG=3200)
    security_domains: Optional[list[str]] = [
        "localhost:3100",
        "127.0.0.1:3100",
        "localhost:3200",
        "127.0.0.1:3200",
    ]


def get_environment_config() -> EnvironmentConfig:
    """
    Load environment configuration from YAML file, then override with environment variables.

    Priority order (highest to lowest):
    1. Environment variables (DATABASE_URL, REDIS_URL, etc.)
    2. YAML file values
    3. Default values
    """

    # Determine environment and config file
    if IS_PROD:
        config_file = "config.prod.yaml"
    elif IS_TEST:
        config_file = "config.test.yaml"
    else:
        config_file = "config.dev.yaml"

    print(f"Loading config file: {config_file}")

    # Get config file path
    config_path = Path(__file__).parent / config_file

    # Load base config from YAML
    if config_path.exists():
        try:
            config = parse_yaml_file_as(EnvironmentConfig, config_path)
        except Exception as e:
            print(f"Warning: Failed to load {config_file}: {e}")
            print("Using default configuration")
            config = EnvironmentConfig()
    else:
        print(f"Warning: Config file {config_file} not found, using defaults")
        config = EnvironmentConfig()

    # Universal environment variable override system
    # Automatically maps ENV vars to config using dot notation
    # Example: EMAIL__HOST -> config.email.host
    #          API_KEYS__OPENAI -> config.api_keys.openai
    env_overrides = []

    # Iterate through all environment variables
    for env_key, env_value in os.environ.items():
        # Check if it's a config variable (contains __)
        if '__' not in env_key:
            continue

        # Split by __ to get path (e.g., EMAIL__HOST -> ['email', 'host'])
        parts = env_key.lower().split('__')

        # Navigate through config object
        try:
            obj = config
            # Navigate to parent object
            for part in parts[:-1]:
                obj = getattr(obj, part)

            # Get the field name and current value
            field_name = parts[-1]
            if not hasattr(obj, field_name):
                continue

            # Get field type for type conversion
            field_type = type(getattr(obj, field_name))

            # Convert value to appropriate type
            if field_type == bool:
                converted_value = env_value.lower() in ('true', '1', 'yes')
            elif field_type == int:
                converted_value = int(env_value)
            elif field_type == float:
                converted_value = float(env_value)
            else:
                converted_value = env_value

            # Set the value
            setattr(obj, field_name, converted_value)
            env_overrides.append(env_key)

        except (AttributeError, ValueError, TypeError):
            # Skip if path doesn't exist or conversion fails
            continue

    if env_overrides:
        print(f"✅ Environment variables override YAML: {', '.join(env_overrides)}")

    return config


# Global environment configuration instance
env = get_environment_config()
