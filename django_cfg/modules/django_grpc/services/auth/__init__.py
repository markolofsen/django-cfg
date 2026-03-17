"""django_grpc.services.auth — JWT authentication, session tokens, and request context."""

try:
    from .jwt_auth import JWTAuthInterceptor, decode_jwt
    _HAS_GRPC = True
except ImportError:
    _HAS_GRPC = False

from .context import (
    get_current_grpc_user,
    set_current_grpc_user,
)
from .session_token import (
    issue_session_token,
    verify_session_token,
    revoke_session_tokens,
)
from .guards import require_session_access

__all__ = [
    # Interceptor
    "JWTAuthInterceptor",
    "decode_jwt",
    # Context accessors
    "get_current_grpc_user",
    "set_current_grpc_user",
    # Session tokens
    "issue_session_token",
    "verify_session_token",
    "revoke_session_tokens",
    # Guards
    "require_session_access",
]
