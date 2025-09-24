"""
Service configuration models for django_cfg.

Following CRITICAL_REQUIREMENTS.md:
- No raw Dict/Any usage - everything through Pydantic models
- Specialized models for each service type (Email, Telegram, etc.)
- Proper validation and type safety
- Environment-aware backend selection
"""

from typing import Dict, Optional, Any, Literal, List
from pydantic import BaseModel, Field, field_validator, model_validator, EmailStr
from pathlib import Path

from django_cfg.core.exceptions import ConfigurationError, ValidationError


class EmailConfig(BaseModel):
    """
    Type-safe email service configuration.
    
    Supports SMTP, console, and file backends with automatic selection
    based on environment and configuration completeness.
    """
    
    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True,
        "extra": "forbid",
    }
    
    # SMTP settings
    host: str = Field(
        default="localhost",
        description="SMTP server hostname",
        min_length=1,
    )
    
    port: int = Field(
        default=587,
        description="SMTP server port",
        ge=1,
        le=65535,
    )
    
    username: Optional[str] = Field(
        default=None,
        description="SMTP username",
    )
    
    password: Optional[str] = Field(
        default=None,
        description="SMTP password",
        repr=False,  # Don't show in repr for security
    )
    
    # Security settings
    use_tls: bool = Field(
        default=True,
        description="Use TLS encryption",
    )
    
    use_ssl: bool = Field(
        default=False,
        description="Use SSL encryption (alternative to TLS)",
    )
    
    # Email settings
    default_from_email: EmailStr = Field(
        default="webmaster@localhost",
        description="Default sender email address",
    )
    
    default_from_name: str = Field(
        default="Django Application",
        description="Default sender name",
        max_length=100,
    )
    
    # Connection settings
    timeout: int = Field(
        default=30,
        description="SMTP connection timeout in seconds",
        ge=1,
        le=300,
    )
    
    # File backend settings (for development)
    file_path: Optional[Path] = Field(
        default=None,
        description="File path for file-based email backend",
    )
    
    # Backend override (for testing)
    backend_override: Optional[str] = Field(
        default=None,
        description="Override automatic backend selection",
        exclude=True,
    )
    
    @field_validator('port')
    @classmethod
    def validate_port(cls, v: int) -> int:
        """Validate SMTP port ranges."""
        # Common SMTP ports
        common_ports = {25, 465, 587, 2525}
        
        if v not in common_ports and v < 1024:
            # Warn about unusual low ports (but don't fail)
            pass
        
        return v
    
    @model_validator(mode='after')
    def validate_security_settings(self) -> 'EmailConfig':
        """Validate email security configuration."""
        if self.use_tls and self.use_ssl:
            raise ValueError("Cannot use both TLS and SSL simultaneously")
        
        # Validate port/security combinations
        if self.port == 465 and not self.use_ssl:
            # Port 465 typically uses SSL
            pass  # Just a note, not enforced
        
        if self.port == 587 and not self.use_tls:
            # Port 587 typically uses TLS
            pass  # Just a note, not enforced
        
        # Validate authentication requirements
        if self.username and not self.password:
            raise ValueError("Password is required when username is provided")
        
        return self
    
    def get_backend_type(self, environment: str, debug: bool) -> str:
        """
        Determine appropriate email backend based on environment.
        
        Args:
            environment: Current environment
            debug: Django DEBUG setting
            
        Returns:
            Django email backend class path
        """
        if self.backend_override:
            return self.backend_override
        
        # Environment-based backend selection
        if environment == "testing":
            return "django.core.mail.backends.locmem.EmailBackend"
        
        elif environment == "development" or debug:
            # Development: Use SMTP if configured, otherwise console
            if self.username and self.password:
                return "django.core.mail.backends.smtp.EmailBackend"
            elif self.file_path:
                return "django.core.mail.backends.filebased.EmailBackend"
            else:
                return "django.core.mail.backends.console.EmailBackend"
        
        elif environment in ("production", "staging"):
            # Production should use SMTP if configured
            if self.username and self.password:
                return "django.core.mail.backends.smtp.EmailBackend"
            else:
                # Fallback to console for incomplete SMTP config
                return "django.core.mail.backends.console.EmailBackend"
        
        else:
            # Default to SMTP if credentials available
            if self.username and self.password:
                return "django.core.mail.backends.smtp.EmailBackend"
            else:
                return "django.core.mail.backends.console.EmailBackend"
    
    def to_django_config(self, environment: str, debug: bool) -> Dict[str, Any]:
        """
        Convert to Django email configuration.
        
        Args:
            environment: Current environment
            debug: Django DEBUG setting
            
        Returns:
            Django email settings dictionary
        """
        backend = self.get_backend_type(environment, debug)
        
        config = {
            'EMAIL_BACKEND': backend,
            'DEFAULT_FROM_EMAIL': str(self.default_from_email),
            'EMAIL_TIMEOUT': self.timeout,
        }
        
        # Add sender name to default from email if specified
        if self.default_from_name and self.default_from_name != "Django Application":
            config['DEFAULT_FROM_EMAIL'] = f"{self.default_from_name} <{self.default_from_email}>"
        
        # Backend-specific settings
        if backend == "django.core.mail.backends.smtp.EmailBackend":
            config.update({
                'EMAIL_HOST': self.host,
                'EMAIL_PORT': self.port,
                'EMAIL_USE_TLS': self.use_tls,
                'EMAIL_USE_SSL': self.use_ssl,
            })
            
            if self.username:
                config['EMAIL_HOST_USER'] = self.username
            
            if self.password:
                config['EMAIL_HOST_PASSWORD'] = self.password
        
        elif backend == "django.core.mail.backends.filebased.EmailBackend":
            if self.file_path:
                config['EMAIL_FILE_PATH'] = str(self.file_path)
            else:
                config['EMAIL_FILE_PATH'] = "tmp/app-messages"
        
        return config


class TelegramConfig(BaseModel):
    """
    Type-safe Telegram bot configuration.
    
    Supports Telegram Bot API for notifications and alerts.
    """
    
    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True,
        "extra": "forbid",
    }
    
    # Bot configuration
    bot_token: str = Field(
        ...,
        description="Telegram bot token from @BotFather",
        min_length=10,
        repr=False,  # Don't show in repr for security
    )
    
    chat_id: int = Field(
        ...,
        description="Telegram chat ID for notifications",
    )
    
    # Message settings
    parse_mode: Literal["HTML", "Markdown", "MarkdownV2", None] = Field(
        default="HTML",
        description="Message parse mode",
    )
    
    disable_notification: bool = Field(
        default=False,
        description="Send messages silently",
    )
    
    disable_web_page_preview: bool = Field(
        default=False,
        description="Disable link previews in messages",
    )
    
    # Connection settings
    timeout: int = Field(
        default=30,
        description="Request timeout in seconds",
        ge=1,
        le=300,
    )
    
    # Webhook settings (optional)
    webhook_url: Optional[str] = Field(
        default=None,
        description="Webhook URL for receiving updates",
    )
    
    webhook_secret: Optional[str] = Field(
        default=None,
        description="Webhook secret token",
        repr=False,
    )
    
    # Rate limiting
    max_retries: int = Field(
        default=3,
        description="Maximum retry attempts for failed requests",
        ge=0,
        le=10,
    )
    
    retry_delay: float = Field(
        default=1.0,
        description="Delay between retry attempts in seconds",
        ge=0.1,
        le=60.0,
    )
    
    @field_validator('bot_token')
    @classmethod
    def validate_bot_token(cls, v: str) -> str:
        """Validate Telegram bot token format."""
        # Basic format validation: should be digits:alphanumeric
        if ':' not in v:
            raise ValueError("Invalid bot token format: missing ':' separator")
        
        parts = v.split(':', 1)
        if len(parts) != 2:
            raise ValueError("Invalid bot token format: should be 'bot_id:token'")
        
        bot_id, token = parts
        
        # Validate bot ID (should be numeric)
        if not bot_id.isdigit():
            raise ValueError("Invalid bot token: bot ID must be numeric")
        
        # Validate token length (should be around 35 characters)
        if len(token) < 30:
            raise ValueError("Invalid bot token: token too short")
        
        return v
    
    @field_validator('chat_id')
    @classmethod
    def validate_chat_id(cls, v: int) -> int:
        """Validate Telegram chat ID."""
        # Chat IDs can be negative (groups/channels) or positive (users)
        # Just check it's not zero
        if v == 0:
            raise ValueError("Chat ID cannot be zero")
        
        return v
    
    @field_validator('webhook_url')
    @classmethod
    def validate_webhook_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate webhook URL format."""
        if v is None:
            return v
        
        if not v.startswith('https://'):
            raise ValueError("Webhook URL must use HTTPS")
        
        from urllib.parse import urlparse
        try:
            parsed = urlparse(v)
            if not parsed.netloc:
                raise ValueError("Invalid webhook URL: missing domain")
        except Exception as e:
            raise ValueError(f"Invalid webhook URL: {e}") from e
        
        return v
    
    def to_config_dict(self) -> Dict[str, Any]:
        """
        Convert to configuration dictionary.
        
        Returns:
            Telegram configuration dictionary
        """
        config = {
            'bot_token': self.bot_token,
            'chat_id': self.chat_id,
            'parse_mode': self.parse_mode,
            'disable_notification': self.disable_notification,
            'disable_web_page_preview': self.disable_web_page_preview,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
        }
        
        if self.webhook_url:
            config['webhook_url'] = self.webhook_url
        
        if self.webhook_secret:
            config['webhook_secret'] = self.webhook_secret
        
        return config


class ServiceConfig(BaseModel):
    """
    Generic service configuration for custom services.
    
    This is a fallback for services that don't have specialized models.
    Prefer specific models like EmailConfig, TelegramConfig when available.
    """
    
    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True,
        "extra": "allow",  # Allow additional fields for flexibility
    }
    
    name: str = Field(
        ...,
        description="Service name",
        min_length=1,
        max_length=50,
    )
    
    enabled: bool = Field(
        default=True,
        description="Whether service is enabled",
    )
    
    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Service-specific configuration",
    )
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate service name format."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError(
                "Service name must contain only alphanumeric characters, "
                "underscores, and hyphens"
            )
        
        return v
    
    def to_config_dict(self) -> Dict[str, Any]:
        """Convert to configuration dictionary."""
        return {
            'name': self.name,
            'enabled': self.enabled,
            **self.config,
        }


# Export all models
__all__ = [
    "EmailConfig",
    "TelegramConfig", 
    "ServiceConfig",
]
