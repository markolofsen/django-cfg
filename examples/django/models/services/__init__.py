"""
Service configuration models for django_cfg.

Provides type-safe configuration for various services:
- EmailConfig: Email/SMTP configuration
- TelegramConfig: Telegram bot configuration
- ServiceConfig: Generic service configuration
"""

from .email import EmailConfig
from .telegram import TelegramConfig
from .base import ServiceConfig

__all__ = [
    "EmailConfig",
    "TelegramConfig",
    "ServiceConfig",
]
