"""
JWT Configuration for Django CFG
Type-safe JWT authentication configuration with Pydantic v2

This model is the START of the auth chain (config → Django settings → token
mint → request verification → frontend client). For the full end-to-end map,
DPoP (RFC 9449) flow, and the auth-class-bypass gotcha, see:
    @docs/architecture/security/auth-logic-chain.md
Related code: middleware/dpop.py, middleware/authentication.py.
"""

from datetime import timedelta
from typing import Any, Dict, Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field, field_validator


class JWTConfig(BaseModel):
    """
    🔐 JWT Authentication Configuration
    
    Provides type-safe JWT token configuration with environment-aware defaults.
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    # === Token Lifetimes ===
    # Secure-by-default: short access + long refresh. Consumers can just write
    # `JWTConfig()` and inherit the recommended posture — no need to restate it.
    access_token_lifetime_minutes: Optional[int] = Field(
        default=30,
        ge=1,
        le=525600,  # 1 year max
        description=(
            "Access token lifetime in MINUTES (default 30; None = maximum 1 year). "
            "Keep this short and pair it with a long refresh token: a stolen access "
            "token expires fast while the user stays logged in via refresh."
        )
    )

    refresh_token_lifetime_days: Optional[int] = Field(
        default=90,
        ge=1,
        le=365,  # 1 year max
        description=(
            "Refresh token lifetime in days (default 90; None = maximum 365). "
            "Long-lived so users 'log in once' and aren't logged out; rotation + "
            "blacklist (below) revoke a reused/stolen refresh token."
        )
    )

    # === Token Rotation ===
    rotate_refresh_tokens: bool = Field(
        default=True,
        description="Rotate refresh tokens on each use"
    )

    blacklist_after_rotation: bool = Field(
        default=True,
        description="Blacklist old tokens after rotation"
    )

    # === Security Settings ===
    algorithm: str = Field(
        default="HS256",
        description="JWT signing algorithm"
    )

    update_last_login: bool = Field(
        default=True,
        description="Update user's last login on token refresh"
    )

    # === Token Claims ===
    user_id_field: str = Field(
        default="id",
        description="User model field for user ID claim"
    )

    user_id_claim: str = Field(
        default="user_id",
        description="JWT claim name for user ID"
    )

    token_type_claim: str = Field(
        default="token_type",
        description="JWT claim name for token type"
    )

    jti_claim: str = Field(
        default="jti",
        description="JWT claim name for token ID"
    )

    # === Authentication Headers ===
    auth_header_types: Tuple[str, ...] = Field(
        default=("Bearer",),
        description="Accepted authentication header types"
    )

    auth_header_name: str = Field(
        default="HTTP_AUTHORIZATION",
        description="HTTP header name for authentication"
    )

    # === DPoP (RFC 9449) — sender-constrained tokens ===
    dpop_enabled: bool = Field(
        default=False,
        description=(
            "Enable DPoP-lite (RFC 9449): bind access tokens to a client-held "
            "non-extractable key so a stolen token is useless without the key. "
            "Default OFF — opt-in per project. When ON, the mint endpoints embed "
            "`cnf.jkt` from the login proof and the auth class requires a valid "
            "DPoP proof on every request whose token carries `cnf.jkt`. "
            "Tokens without `cnf` (CLI / server-to-server) keep working as plain "
            "Bearer, so mixed clients are fine."
        )
    )

    # === Advanced Settings ===
    leeway: int = Field(
        default=0,
        ge=0,
        le=300,  # 5 minutes max
        description="Leeway for token expiration in seconds"
    )

    audience: Optional[str] = Field(
        default=None,
        description="JWT audience claim"
    )

    issuer: Optional[str] = Field(
        default=None,
        description="JWT issuer claim"
    )

    @field_validator("algorithm")
    @classmethod
    def validate_algorithm(cls, v: str) -> str:
        """Validate JWT algorithm."""
        allowed_algorithms = [
            "HS256", "HS384", "HS512",
            "RS256", "RS384", "RS512",
            "ES256", "ES384", "ES512"
        ]
        if v not in allowed_algorithms:
            raise ValueError(f"Algorithm must be one of: {', '.join(allowed_algorithms)}")
        return v

    @field_validator("auth_header_types")
    @classmethod
    def validate_auth_header_types(cls, v: Tuple[str, ...]) -> Tuple[str, ...]:
        """Validate authentication header types."""
        if not v:
            raise ValueError("At least one auth header type must be specified")
        return v

    def get_effective_access_token_lifetime(self) -> timedelta:
        """
        Effective access-token lifetime as a timedelta.

        `access_token_lifetime_minutes` is the single knob; None = the 1-year
        maximum. This is the source of truth used by `to_django_settings`.
        """
        minutes = self.access_token_lifetime_minutes
        if minutes is None:
            minutes = 525600  # 1 year
        return timedelta(minutes=minutes)

    def get_effective_refresh_token_days(self) -> int:
        """
        Get effective refresh token lifetime in days.
        
        Returns:
            Refresh token lifetime (365 days if None = maximum)
        """
        return self.refresh_token_lifetime_days if self.refresh_token_lifetime_days is not None else 365

    def to_django_settings(self, secret_key: str) -> Dict[str, Any]:
        """
        Convert to Django SIMPLE_JWT settings.
        
        Args:
            secret_key: Django SECRET_KEY for token signing
            
        Returns:
            Django SIMPLE_JWT configuration dictionary
        """
        return {
            "SIMPLE_JWT": {
                # Token lifetimes
                "ACCESS_TOKEN_LIFETIME": self.get_effective_access_token_lifetime(),
                "REFRESH_TOKEN_LIFETIME": timedelta(days=self.get_effective_refresh_token_days()),

                # Token rotation
                "ROTATE_REFRESH_TOKENS": self.rotate_refresh_tokens,
                "BLACKLIST_AFTER_ROTATION": self.blacklist_after_rotation,

                # Security
                "ALGORITHM": self.algorithm,
                "SIGNING_KEY": secret_key,
                "VERIFYING_KEY": None,
                "UPDATE_LAST_LOGIN": self.update_last_login,

                # Claims
                "USER_ID_FIELD": self.user_id_field,
                "USER_ID_CLAIM": self.user_id_claim,
                "TOKEN_TYPE_CLAIM": self.token_type_claim,
                "JTI_CLAIM": self.jti_claim,

                # Headers
                "AUTH_HEADER_TYPES": self.auth_header_types,
                "AUTH_HEADER_NAME": self.auth_header_name,

                # Advanced
                "LEEWAY": self.leeway,
                "AUDIENCE": self.audience,
                "ISSUER": self.issuer,

                # Additional settings
                "JWK_URL": None,
                "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
                "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
                "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
                "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
                "SLIDING_TOKEN_LIFETIME": self.get_effective_access_token_lifetime(),
                "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=self.get_effective_refresh_token_days()),
            },
            # Top-level flag the DPoP auth layer reads (SIMPLE_JWT is owned by
            # simplejwt and ignores unknown keys, so DPoP config lives outside it).
            "DJANGO_CFG_DPOP_ENABLED": self.dpop_enabled,
        }

# Export the main class
__all__ = [
    "JWTConfig",
]
