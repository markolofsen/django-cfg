"""
Ngrok configuration models for django_cfg.

Simple, type-safe ngrok configuration following KISS principle.
"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field, field_validator
import os


class NgrokAuthConfig(BaseModel):
    """Ngrok authentication configuration."""
    
    authtoken: Optional[str] = Field(
        default=None,
        description="Ngrok auth token (loaded from NGROK_AUTHTOKEN env var if not provided)",
        repr=False  # Don't show in repr for security
    )
    
    authtoken_from_env: bool = Field(
        default=False,  # Changed default to False
        description="Load auth token from NGROK_AUTHTOKEN environment variable"
    )
    
    def get_authtoken(self) -> Optional[str]:
        """Get auth token from config or environment."""
        if self.authtoken:
            return self.authtoken
        
        if self.authtoken_from_env:
            return os.environ.get("NGROK_AUTHTOKEN")
        
        return None


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


class NgrokConfig(BaseModel):
    """Main ngrok configuration for django-cfg."""
    
    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True,
        "extra": "forbid"
    }
    
    enabled: bool = Field(
        default=False,
        description="Enable ngrok integration (only works in DEBUG mode)"
    )
    
    auth: NgrokAuthConfig = Field(
        default_factory=NgrokAuthConfig,
        description="Authentication configuration"
    )
    
    tunnel: NgrokTunnelConfig = Field(
        default_factory=NgrokTunnelConfig,
        description="Tunnel configuration"
    )
    
    auto_start: bool = Field(
        default=True,
        description="Automatically start tunnel with runserver_ngrok command"
    )
    
    update_api_url: bool = Field(
        default=True,
        description="Automatically update api_url with tunnel URL when tunnel is active"
    )
    
    webhook_path: str = Field(
        default="/webhooks/",
        description="Default webhook path for webhook URLs"
    )
    
    @field_validator("enabled")
    @classmethod
    def validate_enabled_in_debug_only(cls, v: bool) -> bool:
        """Ensure ngrok is only enabled in debug mode."""
        if v:
            # Only check if Django is available and fully configured
            try:
                from django.conf import settings
                # Only validate if settings are configured and DEBUG attribute exists
                if settings.configured and hasattr(settings, 'DEBUG') and not settings.DEBUG:
                    raise ValueError("Ngrok can only be enabled in DEBUG mode")
            except (ImportError, AttributeError, RuntimeError):
                # Django not available, not configured, or settings not ready - skip validation
                pass
        return v


# Export models
__all__ = [
    "NgrokConfig",
    "NgrokAuthConfig", 
    "NgrokTunnelConfig",
]
