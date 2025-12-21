"""
Configuration models for django_cfg.

All models are built using Pydantic v2 for complete type safety and validation.
Following CRITICAL_REQUIREMENTS.md - no raw Dict/Any usage, everything is properly typed.

Organized by category:
- base/ - Base classes and foundations
- infrastructure/ - Core infrastructure (database, cache, logging, security)
- api/ - API, authentication, and documentation
- django/ - Django-specific configurations
- services/ - External services (email, telegram, ngrok)
- payments/ - Payment provider configurations
- tasks/ - Task/worker configurations
"""

# Base classes
# External modules (imported from other locations)
from ..modules.django_unfold.models.config import UnfoldConfig

# API & Authentication
from .api.config import APIConfig
from .api.cors import CORSConfig
from .api.drf.config import DRFConfig
from .api.drf.redoc import RedocUISettings
from .api.drf.spectacular import SpectacularConfig
from .api.drf.swagger import SwaggerUISettings
from .api.jwt import JWTConfig
from .api.keys import ApiKeys
from .api.limits import LimitsConfig
from .api.oauth import GitHubOAuthConfig, OAuthConfig
from .api.twofactor import TwoFactorConfig
from .base.config import BaseConfig, BaseSettings
from .base.module import BaseCfgAutoModule

# Django-specific
from .django.axes import AxesConfig
from .django.constance import ConstanceConfig, ConstanceField
from .django.crypto_fields import CryptoFieldsConfig
from .django.django_rq import DjangoRQConfig, RQQueueConfig
from .django.environment import EnvironmentConfig
from .django.openapi import OpenAPIClientConfig
from .infrastructure.cache import CacheConfig

# Infrastructure
from .infrastructure.backup import (
    BackupConfig,
    BackupDatabaseConfig,
    BackupRetentionConfig,
    BackupScheduleConfig,
    BackupStorageConfig,
)
from .infrastructure.database import DatabaseConfig
from .infrastructure.logging import LoggingConfig
from .infrastructure.security import SecurityConfig
from .ngrok.auth import NgrokAuthConfig
from .ngrok.config import NgrokConfig
from .ngrok.tunnel import NgrokTunnelConfig

# Payments
from .payments.config import PaymentsConfig, NowPaymentsConfig
from .services.base import ServiceConfig

# Services
from .services.email import EmailConfig
from .services.telegram import TelegramConfig

__all__ = [
    # Base
    "BaseConfig",
    "BaseSettings",
    "BaseCfgAutoModule",
    # Infrastructure
    "BackupConfig",
    "BackupDatabaseConfig",
    "BackupRetentionConfig",
    "BackupScheduleConfig",
    "BackupStorageConfig",
    "CacheConfig",
    "DatabaseConfig",
    "LoggingConfig",
    "SecurityConfig",
    # API
    "APIConfig",
    "ApiKeys",
    "JWTConfig",
    "CORSConfig",
    "LimitsConfig",
    "DRFConfig",
    "SpectacularConfig",
    "SwaggerUISettings",
    "RedocUISettings",
    # Django
    "EnvironmentConfig",
    "ConstanceConfig",
    "ConstanceField",
    "DjangoRQConfig",
    "RQQueueConfig",
    "OpenAPIClientConfig",
    "UnfoldConfig",
    "AxesConfig",
    "CryptoFieldsConfig",
    # Services
    "EmailConfig",
    "TelegramConfig",
    "ServiceConfig",
    "NgrokConfig",
    "NgrokAuthConfig",
    "NgrokTunnelConfig",
    # Payments
    "PaymentsConfig",
    "NowPaymentsConfig",
    # OAuth
    "GitHubOAuthConfig",
    "OAuthConfig",
    # 2FA
    "TwoFactorConfig",
]
