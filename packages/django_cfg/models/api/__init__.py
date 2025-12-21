"""
API configuration models for django_cfg.

API, authentication, and documentation configuration.
"""

from .config import APIConfig
from .cors import CORSConfig
from .drf.config import DRFConfig
from .drf.redoc import RedocUISettings
from .drf.spectacular import SpectacularConfig
from .drf.swagger import SwaggerUISettings
from .jwt import JWTConfig
from .keys import ApiKeys
from .limits import LimitsConfig
from .oauth import GitHubOAuthConfig, OAuthConfig
from .rate_limiting import RateLimitConfig, RateLimitRule
from .twofactor import TwoFactorConfig
from .webpush import WebPushConfig

__all__ = [
    "APIConfig",
    "ApiKeys",
    "JWTConfig",
    "CORSConfig",
    "LimitsConfig",
    "RateLimitConfig",
    "RateLimitRule",
    "DRFConfig",
    "SpectacularConfig",
    "SwaggerUISettings",
    "RedocUISettings",
    "GitHubOAuthConfig",
    "OAuthConfig",
    "TwoFactorConfig",
    "WebPushConfig",
]
