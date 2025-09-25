"""
Environment Configuration Loader for Django CFG Sample

Loads environment-specific configuration from YAML files using pydantic-yaml.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, computed_field
from pydantic_yaml import parse_yaml_file_as
from enum import Enum

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
    
    url: str = "sqlite:///db.sqlite3"
    url_blog: str = "sqlite:///blog.sqlite3"
    url_shop: str = "sqlite:///shop.sqlite3"


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

class PaymentsConfig(BaseModel):
    """Payments configuration."""
    
    nowpayments_api_key: str = ""
    nowpayments_ipn_secret: str = ""
    cryptapi_btc_address: str = ""
    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    stripe_webhook_secret: str = ""
    cryptomus_api_key: str = ""
    cryptomus_merchant_uuid: str = ""


class ApiKeysConfig(BaseModel):
    """API keys configuration."""
    
    ngrok_api_key: str = ""
    cloudflare_api_key: str = ""
    openrouter_api_key: str = ""
    openai_api_key: str = ""
    sendgrid_api_key: str = ""
    
    payments: PaymentsConfig = Field(default_factory=PaymentsConfig)

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
    twilio: TwilioConfig = Field(default_factory=TwilioConfig)
    app: AppConfig = Field(default_factory=AppConfig)
    env: EnvironmentMode = Field(default_factory=EnvironmentMode)
    
    # Cache
    redis_url: Optional[str] = None
    
    # Security
    ssl_redirect: Optional[bool] = None
    security_domains: Optional[list[str]] = None


def get_environment_config() -> EnvironmentConfig:
    """Load environment configuration from YAML file."""
    
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
            
    
    # Get config file path
    config_path = Path(__file__).parent / config_file
    
    if config_path.exists():
        try:
            return parse_yaml_file_as(EnvironmentConfig, config_path)
        except Exception as e:
            print(f"Warning: Failed to load {config_file}: {e}")
            print("Using default configuration")
    else:
        print(f"Warning: Config file {config_file} not found, using defaults")
    
    # Return default configuration
    return EnvironmentConfig()


# Global environment configuration instance
env = get_environment_config()
