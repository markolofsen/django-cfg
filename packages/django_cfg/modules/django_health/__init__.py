"""
Django Health Check Module for django_cfg.

Auto-configuring health check endpoints.
"""

from .service import DjangoHealth

__all__ = ["DjangoHealth"]
