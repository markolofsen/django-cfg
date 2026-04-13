"""MCP Context Management."""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class MCPContext:
    """
    Context object passed to all MCP tools.

    Contains user, request, session info, and configuration.
    Similar to RunContext in Pydantic-AI.
    """
    user: Any  # Django User object or AnonymousUser
    request: Any  # Django HttpRequest
    session_key: str
    config: Any  # MCPConfig object

    # Future: add database session, cache, etc.

    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.user and self.user.is_authenticated

    def is_staff(self) -> bool:
        """Check if user is staff."""
        return self.user and getattr(self.user, "is_staff", False)

    def has_perm(self, perm: str) -> bool:
        """Check if user has permission."""
        if not self.user:
            return False
        return self.user.has_perm(perm)
