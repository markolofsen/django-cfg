"""
Ngrok tunnel configuration.
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class NgrokTunnelConfig(BaseModel):
    """Configuration for ngrok tunnel."""

    domain: Optional[str] = Field(
        default=None,
        description="Custom domain for tunnel (requires paid ngrok plan)"
    )

    schemes: List[Literal["http", "https"]] = Field(
        default_factory=lambda: ["http", "https"],
        description="URL schemes to tunnel"
    )

    basic_auth: Optional[List[str]] = Field(
        default=None,
        description="Basic auth credentials in format ['user:pass']"
    )

    compression: bool = Field(
        default=True,
        description="Enable gzip compression"
    )


__all__ = [
    "NgrokTunnelConfig",
]
