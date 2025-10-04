"""
Utility Functions and Classes.

Authentication, version checking, and helper utilities.

Example:
    >>> from django_ipc.utils import AuthManager, JWTAuthenticator
    >>> from django_ipc.utils import check_version, display_startup_banner
"""

from .auth import (
    AuthenticationError,
    JWTAuthenticator,
    TokenAuthenticator,
    NoAuthenticator,
    AuthManager,
)
from .version_checker import (
    check_version,
    display_update_warning,
    display_startup_banner,
    get_current_version,
    is_outdated,
)

__all__ = [
    # Auth
    "AuthenticationError",
    "JWTAuthenticator",
    "TokenAuthenticator",
    "NoAuthenticator",
    "AuthManager",
    # Version checking
    "check_version",
    "display_update_warning",
    "display_startup_banner",
    "get_current_version",
    "is_outdated",
]
