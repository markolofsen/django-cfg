"""
Integration generators module.

Contains generators for third-party integrations and frameworks:
- Session configuration
- External services (Telegram, Unfold, Constance)
- API frameworks (JWT, DRF, Spectacular, OpenAPI Client)
- Background tasks (ReArq)
- Task scheduling (django-q2)
- Tailwind CSS configuration
"""

from .api import APIFrameworksGenerator
from .django_q2 import DjangoQ2SettingsGenerator
from .sessions import SessionSettingsGenerator
from .tasks import TasksSettingsGenerator
from .third_party import ThirdPartyIntegrationsGenerator

__all__ = [
    "SessionSettingsGenerator",
    "ThirdPartyIntegrationsGenerator",
    "APIFrameworksGenerator",
    "TasksSettingsGenerator",
    "DjangoQ2SettingsGenerator",
]
