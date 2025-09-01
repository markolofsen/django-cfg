"""
Environment Configuration Loader for Django CFG Sample

Loads environment-specific configuration from YAML files using pydantic-yaml.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
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


class AppConfig(BaseModel):
    """Application configuration."""
    
    name: str = "Django CFG Sample"
    domain: str = "localhost"
    api_url: str = "http://localhost:8000"
    site_url: str = "http://localhost:3000"


class EnvironmentFlags(BaseModel):
    """Environment flags."""
    
    is_docker: bool = False
    is_dev: bool = True
    is_prod: bool = False
    debug: bool = True


class EnvironmentConfig(BaseModel):
    """Complete environment configuration."""
    
    # Core Django settings
    secret_key: str = "django-cfg-sample-secret-key-change-in-production"
    debug: bool = True
    
    # Configuration sections
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    email: EmailConfig = Field(default_factory=EmailConfig)
    telegram: TelegramConfig = Field(default_factory=TelegramConfig)
    app: AppConfig = Field(default_factory=AppConfig)
    env: EnvironmentFlags = Field(default_factory=EnvironmentFlags)
    
    # Cache
    redis_url: Optional[str] = None


def get_environment_config() -> EnvironmentConfig:
    """Load environment configuration from YAML file."""
    
    # Determine environment
    if IS_PROD:
        config_file = "config.prod.yaml"
    elif IS_TEST:
        config_file = "config.test.yaml"
    else:
        config_file = "config.dev.yaml"
    
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
