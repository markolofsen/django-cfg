"""
Django-CFG Common Mixins.

Shared mixins for DRF views and viewsets.
"""
from .admin_api import AdminAPIMixin
from .client_api import ClientAPIMixin

__all__ = [
    "AdminAPIMixin",
    "ClientAPIMixin",
]
