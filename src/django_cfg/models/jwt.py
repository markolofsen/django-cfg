"""
JWT Configuration for Django CFG
Type-safe JWT authentication configuration with Pydantic v2
"""

from typing import Dict, Any, Optional, Tuple
from datetime import timedelta
from pydantic import BaseModel, Field, ConfigDict, field_validator


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
    access_token_lifetime_hours: int = Field(
        default=24,
        ge=1,
        le=8760,  # 1 year max
        description="Access token lifetime in hours"
    )
    
    refresh_token_lifetime_days: int = Field(
        default=30,
        ge=1,
        le=365,  # 1 year max
        description="Refresh token lifetime in days"
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
    
    def configure_for_environment(self, environment: str, debug: bool = False) -> "JWTConfig":
        """
        Configure JWT settings based on environment.
        
        Args:
            environment: Environment name (development, production, etc.)
            debug: Debug mode flag
            
        Returns:
            New JWTConfig instance with environment-specific settings
        """
        config_data = self.model_dump()
        
        if environment == "development" or debug:
            # Development: shorter tokens for security
            config_data.update({
                "access_token_lifetime_hours": 1,
                "refresh_token_lifetime_days": 7,
                "leeway": 30,  # More lenient for development
            })
        elif environment == "production":
            # Production: longer tokens for user experience
            config_data.update({
                "access_token_lifetime_hours": 24,
                "refresh_token_lifetime_days": 30,
                "leeway": 0,  # Strict for production
            })
        elif environment == "testing":
            # Testing: very short tokens
            config_data.update({
                "access_token_lifetime_hours": 1,
                "refresh_token_lifetime_days": 1,
                "rotate_refresh_tokens": False,  # Simpler for tests
                "blacklist_after_rotation": False,
            })
        
        return self.__class__(**config_data)
    
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
                "ACCESS_TOKEN_LIFETIME": timedelta(hours=self.access_token_lifetime_hours),
                "REFRESH_TOKEN_LIFETIME": timedelta(days=self.refresh_token_lifetime_days),
                
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
                "SLIDING_TOKEN_LIFETIME": timedelta(hours=self.access_token_lifetime_hours),
                "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=self.refresh_token_lifetime_days),
            }
        }
    
    def get_token_info(self) -> Dict[str, str]:
        """
        Get human-readable token lifetime information.
        
        Returns:
            Dictionary with token lifetime descriptions
        """
        return {
            "access_token": f"{self.access_token_lifetime_hours} hour{'s' if self.access_token_lifetime_hours != 1 else ''}",
            "refresh_token": f"{self.refresh_token_lifetime_days} day{'s' if self.refresh_token_lifetime_days != 1 else ''}",
            "algorithm": self.algorithm,
            "rotation": "enabled" if self.rotate_refresh_tokens else "disabled",
        }


# Export the main class
__all__ = [
    "JWTConfig",
]
