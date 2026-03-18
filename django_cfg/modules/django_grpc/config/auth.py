"""django_grpc.config.auth — gRPC auth configuration."""

from __future__ import annotations

import secrets
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

# A3: Allowlist of secure JWT algorithms. Free-form str accepted "none" and typos silently.
# "none" would bypass signature verification entirely; typos cause all JWT decodes to fail.
JwtAlgorithm = Literal["HS256", "HS384", "HS512", "RS256", "RS384", "RS512", "ES256", "ES384", "ES512"]


class GrpcAuthConfig(BaseModel):
    """gRPC JWT auth configuration."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    enabled: bool = Field(default=True)
    require_auth: bool = Field(
        default=False,
        description="False = anonymous access allowed",
    )
    jwt_algorithm: JwtAlgorithm = Field(default="HS256", description="JWT signing algorithm (allowlisted)")
    jwt_expiration_hours: int = Field(default=24, ge=1, le=8760)

    public_methods: list[str] = Field(
        default_factory=list,
        description="Full method paths excluded from auth",
    )

    internal_secret: str | None = Field(
        default=None,
        description=(
            "Shared secret for internal Django→gRPC calls. "
            "Sent as x-internal-secret metadata. Auto-generated per-process if None."
        ),
    )

    session_token_ttl: int = Field(
        default=86400,
        ge=60,
        le=604800,
        description="Session token TTL in seconds (default 24h, max 7d)",
    )

    interceptor_class: str = Field(
        default="",
        description=(
            "Import path to a custom grpc.aio.ServerInterceptor class that replaces "
            "the built-in JWTAuthInterceptor. Use when the application has its own "
            "auth scheme (e.g., API keys, CLI tokens). Empty = use built-in JWT."
        ),
    )

    @model_validator(mode="after")
    def _auto_generate_internal_secret(self) -> "GrpcAuthConfig":
        """Auto-generate internal_secret per-process if not explicitly set."""
        if self.internal_secret is None:
            object.__setattr__(self, "internal_secret", secrets.token_hex(32))
        return self


__all__ = ["GrpcAuthConfig"]
