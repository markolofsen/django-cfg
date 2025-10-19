"""
Service configuration models for django_cfg.

Provides type-safe configuration for various services:
- EmailConfig: Email/SMTP configuration
- TelegramConfig: Telegram bot configuration
- ServiceConfig: Generic service configuration
"""

from .base import ServiceConfig
from .email import EmailConfig
from .telegram import TelegramConfig

__all__ = [
    "EmailConfig",
    "TelegramConfig",
    "ServiceConfig",
]
