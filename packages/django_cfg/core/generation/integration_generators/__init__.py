"""
Integration generators module.

Contains generators for third-party integrations and frameworks:
- Session configuration
- External services (Telegram, Unfold, Constance)
- API frameworks (JWT, DRF, Spectacular, OpenAPI Client)
- Background tasks (ReArq)
- Crontab scheduling (django-crontab)
"""

from .api import APIFrameworksGenerator
from .crontab import CrontabSettingsGenerator
from .sessions import SessionSettingsGenerator
from .tasks import TasksSettingsGenerator
from .third_party import ThirdPartyIntegrationsGenerator

__all__ = [
    "SessionSettingsGenerator",
    "ThirdPartyIntegrationsGenerator",
    "APIFrameworksGenerator",
    "TasksSettingsGenerator",
    "CrontabSettingsGenerator",
]
