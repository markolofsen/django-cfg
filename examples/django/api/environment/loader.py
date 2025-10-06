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


class TwilioConfig(BaseModel):
    """Twilio configuration."""

    account_sid: str = ""
    auth_token: str = ""
    whatsapp_from: str = ""
    sms_from: str = ""
    sendgrid_api_key: str = ""
    verify_service_sid: str = ""
    otp_template_id: Optional[str] = None
    otp_from_email: Optional[str] = None


class ApiKeysConfig(BaseModel):
    """API keys configuration."""

    ngrok: str = ""
    cloudflare: str = ""
    openrouter: str = ""
    openai: str = ""
    sendgrid: str = ""


class PaymentsApiKeysConfig(BaseModel):
    """Payments API keys configuration."""

    nowpayments_api_key: str = ""
    nowpayments_ipn_secret: str = ""
    nowpayments_sandbox_mode: bool = True


class AppConfig(BaseModel):
    """Application configuration."""

    name: str = "Django CFG Sample"
    logo_url: str = ""
    domain: str = "localhost"
    api_url: str = "http://localhost:8000"
    site_url: str = "http://localhost:3000"
    dashboard_url: str = "http://localhost:3000/dashboard"
    ticket_url: str = "http://localhost:3000/support/ticket/{uuid}"
    otp_url: str = "http://localhost:3000/auth/otp/{code}"


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
    twilio: TwilioConfig = Field(default_factory=TwilioConfig)
    app: AppConfig = Field(default_factory=AppConfig)
    env: EnvironmentMode = Field(default_factory=EnvironmentMode)

    # Cache
    redis_url: Optional[str] = None

    # Security
    ssl_redirect: Optional[bool] = None
    security_domains: Optional[list[str]] = None


def get_environment_config() -> EnvironmentConfig:
    """
    Load environment configuration from YAML file, then override with environment variables.

    Priority order (highest to lowest):
    1. Environment variables (DATABASE_URL, REDIS_URL, etc.)
    2. YAML file values
    3. Default values
    """

    # Determine environment
    if IS_PROD:
        config_file = "config.prod.yaml"
    elif IS_TEST:
        config_file = "config.test.yaml"
    else:
        config_file = "config.dev.yaml"

        # Just for development purposes (You can ignore this file)
        ignore_file = "config.dev.ignore.yaml"
        if (Path(__file__).parent / ignore_file).exists():
            config_file = ignore_file

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

    # Override with environment variables (Docker-friendly)
    # This allows Docker environment to override YAML values
    env_overrides = []

    if database_url := os.environ.get("DATABASE_URL"):
        config.database.url = database_url
        env_overrides.append("DATABASE_URL")

    if database_url_blog := os.environ.get("DATABASE_URL_BLOG"):
        config.database.url_blog = database_url_blog
        env_overrides.append("DATABASE_URL_BLOG")

    if database_url_shop := os.environ.get("DATABASE_URL_SHOP"):
        config.database.url_shop = database_url_shop
        env_overrides.append("DATABASE_URL_SHOP")

    if redis_url := os.environ.get("REDIS_URL"):
        config.redis_url = redis_url
        env_overrides.append("REDIS_URL")

    if secret_key := os.environ.get("SECRET_KEY"):
        config.secret_key = secret_key
        env_overrides.append("SECRET_KEY")

    # API Keys from environment
    if openai_key := os.environ.get("OPENAI_API_KEY"):
        config.api_keys.openai = openai_key
        env_overrides.append("OPENAI_API_KEY")

    if openrouter_key := os.environ.get("OPENROUTER_API_KEY"):
        config.api_keys.openrouter = openrouter_key
        env_overrides.append("OPENROUTER_API_KEY")

    if ngrok_key := os.environ.get("NGROK_AUTHTOKEN"):
        config.api_keys.ngrok = ngrok_key
        env_overrides.append("NGROK_AUTHTOKEN")

    # Payments API Keys
    if nowpayments_key := os.environ.get("NOWPAYMENTS_API_KEY"):
        config.payments_api_keys.nowpayments_api_key = nowpayments_key
        env_overrides.append("NOWPAYMENTS_API_KEY")

    if nowpayments_secret := os.environ.get("NOWPAYMENTS_IPN_SECRET"):
        config.payments_api_keys.nowpayments_ipn_secret = nowpayments_secret
        env_overrides.append("NOWPAYMENTS_IPN_SECRET")

    if env_overrides:
        print(f"✅ Environment variables override YAML: {', '.join(env_overrides)}")

    return config


# Global environment configuration instance
env = get_environment_config()
