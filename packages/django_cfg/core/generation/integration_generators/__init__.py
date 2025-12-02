"""
Integration generators module.

Contains generators for third-party integrations and frameworks:
- Session configuration
- External services (Telegram, Unfold, Constance)
- API frameworks (JWT, DRF, Spectacular, OpenAPI Client)
- OAuth providers (GitHub, etc.)
- Task scheduling (django-rq)
- Tailwind CSS configuration
"""

from .api import APIFrameworksGenerator
from .django_rq import DjangoRQSettingsGenerator
from .oauth import OAuthSettingsGenerator
from .sessions import SessionSettingsGenerator
from .third_party import ThirdPartyIntegrationsGenerator

__all__ = [
    "SessionSettingsGenerator",
    "ThirdPartyIntegrationsGenerator",
    "APIFrameworksGenerator",
    "DjangoRQSettingsGenerator",
    "OAuthSettingsGenerator",
]
