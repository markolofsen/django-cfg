"""
Django Client - Django integration for openapi_client.

Provides Django management commands and URL integration.
"""

# Django AppConfig
default_app_config = 'django_cfg.modules.django_client.apps.DjangoClientConfig'

# Re-export everything from openapi_client
from django_cfg.modules.django_client.core import *  # noqa

# Django-specific
from .management.commands.generate_client import Command as GenerateClientCommand
from .urls import get_openapi_urls

__all__ = [
    "GenerateClientCommand",
    "get_openapi_urls",
]
