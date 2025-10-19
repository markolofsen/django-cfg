"""
Ngrok authentication configuration.
"""

import os
from typing import Optional

from pydantic import BaseModel, Field


class NgrokAuthConfig(BaseModel):
    """Ngrok authentication configuration."""

    authtoken: Optional[str] = Field(
        default=None,
        description="Ngrok auth token (loaded from NGROK_AUTHTOKEN env var if not provided)",
        repr=False  # Don't show in repr for security
    )

    authtoken_from_env: bool = Field(
        default=True,  # Try to load from env var by default
        description="Load auth token from NGROK_AUTHTOKEN environment variable"
    )

    def get_authtoken(self) -> Optional[str]:
        """Get auth token from config or environment."""
        if self.authtoken:
            return self.authtoken

        if self.authtoken_from_env:
            return os.environ.get("NGROK_AUTHTOKEN")

        return None


__all__ = [
    "NgrokAuthConfig",
]
