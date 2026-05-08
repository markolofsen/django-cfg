"""Managers package for the user account model.

Re-exports the queryset and manager so callers can use
``from django_cfg.apps.system.accounts.managers import UserQuerySet``
without reaching into private module paths.
"""

from .user_manager import UserManager
from .user_queryset import UserQuerySet

__all__ = ["UserManager", "UserQuerySet"]
