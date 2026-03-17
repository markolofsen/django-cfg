"""
django_grpc.services.auth.guards — Session access guard for gRPC handlers.

Reusable guard callable from any gRPC handler to enforce session-level
password protection. Internal calls (``x-internal-secret``) never reach
guards — they are bypassed at the interceptor level.

Usage in a gRPC handler::

    async def SendInput(self, request, context):
        if not await require_session_access(
            request.session_id, context, self._check_password_required,
        ):
            return SendInputResponse(success=False, error="Access denied")
        # ... existing logic
"""

from __future__ import annotations

import logging
from typing import Awaitable, Callable, Optional, Union

from .session_token import verify_session_token

logger = logging.getLogger(__name__)

# Callback type: async (session_id) -> bool (is password required for this session?)
PasswordCheckCallback = Callable[[str], Union[bool, Awaitable[bool]]]


async def require_session_access(
    session_id: str,
    context: object,
    password_check_callback: Optional[PasswordCheckCallback] = None,
) -> bool:
    """Check session access for external callers.

    Internal calls (``x-internal-secret``) are bypassed at the interceptor
    level and never reach this guard.

    Args:
        session_id: The session to check access for.
        context: ``grpc.aio.ServicerContext`` instance.
        password_check_callback: Optional async/sync callable that returns
            True if the session requires password protection.

    Returns:
        True if access is allowed. False if denied (context is aborted).
    """
    import inspect

    try:
        import grpc
    except ImportError:
        return True

    # No callback means no password enforcement
    if password_check_callback is None:
        return True

    # Ask app if this session requires a password
    result = password_check_callback(session_id)
    if inspect.isawaitable(result):
        requires_password = await result
    else:
        requires_password = result

    if not requires_password:
        return True

    # Extract session token from metadata
    metadata = dict(context.invocation_metadata())  # type: ignore[union-attr]
    session_token = metadata.get("x-session-token", "")
    if isinstance(session_token, bytes):
        session_token = session_token.decode()

    if session_token and verify_session_token(session_id, session_token):
        return True

    # Deny access
    logger.warning("Session access denied: session=%s (no valid session token)", session_id)
    await context.abort(  # type: ignore[union-attr]
        grpc.StatusCode.UNAUTHENTICATED,
        "Session requires password. Authenticate via ConnectTerminal first.",
    )
    return False


__all__ = ["require_session_access", "PasswordCheckCallback"]
