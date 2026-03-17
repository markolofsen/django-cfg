"""
django_grpc.services.auth.context — Async-safe gRPC request context.

ContextVar-based storage for the current gRPC user.
Safe to use in grpc.aio (each request coroutine has its own context copy).

Populated by JWTAuthInterceptor from simplejwt claims:
    user_id  — from "user_id" claim
    email    — from "email" claim (if present in token)
    roles    — from "roles" claim (if present in token)

Usage:
    # In interceptor (write):
    set_current_grpc_user(ctx)

    # In handler / observability (read):
    user = get_current_grpc_user()   # GrpcUserContext | None
"""

from __future__ import annotations

import contextvars
from typing import List, Optional

try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict  # type: ignore[assignment]


class GrpcUserContext(TypedDict, total=False):
    """Typed context for the authenticated gRPC user, set by JWTAuthInterceptor."""
    user_id:          Optional[int]   # from JWT "user_id" claim
    email:            str             # from JWT "email" claim
    roles:            List[str]       # from JWT "roles" claim, e.g. ["admin", "agent"]
    is_authenticated: bool
    is_active:        int             # 1/0
    # A5: safe defaults — missing claims → False (never raises KeyError in handlers)
    is_staff:         bool            # from JWT "is_staff" claim
    is_superuser:     bool            # from JWT "is_superuser" claim


# One ContextVar per process — each grpc.aio request gets its own copy.
# default=None means unauthenticated / anonymous requests return None.
_grpc_user_var: contextvars.ContextVar[Optional[GrpcUserContext]] = contextvars.ContextVar(
    "grpc_user", default=None
)


def get_current_grpc_user() -> Optional[GrpcUserContext]:
    """Return the current request's authenticated user context or None."""
    return _grpc_user_var.get()


def set_current_grpc_user(row: Optional[GrpcUserContext]) -> None:
    """Set the authenticated user context for the current request."""
    _grpc_user_var.set(row)


__all__ = [
    "GrpcUserContext",
    "get_current_grpc_user",
    "set_current_grpc_user",
]
