"""Provider-agnostic OAuth sign-in: one flow, one linking rule, providers behind a registry."""

from .base import OAuthError, OAuthErrorCode, OAuthIdentity, OAuthProvider, TokenSet
from .login import finalize_login
from .registry import all_providers, enabled_providers, get_provider
from .service import LoginResult, OAuthService

__all__ = [
    "LoginResult",
    "OAuthError",
    "OAuthErrorCode",
    "OAuthIdentity",
    "OAuthProvider",
    "OAuthService",
    "TokenSet",
    "all_providers",
    "enabled_providers",
    "finalize_login",
    "get_provider",
]
