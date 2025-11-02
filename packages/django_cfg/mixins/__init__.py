"""
Django-CFG Common Mixins.

Shared mixins for DRF views and viewsets.
"""
from .admin_api import AdminAPIMixin
from .client_api import ClientAPIMixin
from .superadmin_api import SuperAdminAPIMixin

__all__ = [
    "AdminAPIMixin",
    "ClientAPIMixin",
    "SuperAdminAPIMixin",
]
