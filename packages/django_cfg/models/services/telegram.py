"""
Telegram service configuration for django_cfg.

Type-safe Telegram bot configuration with validation.
"""

from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field, field_validator


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
        """Validate webhook URL format. Allows environment variable templates like ${VAR:-default}."""
        if v is None:
            return v

        # Skip validation for environment variable templates
        if v.startswith("${") and "}" in v:
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


__all__ = [
    "TelegramConfig",
]
