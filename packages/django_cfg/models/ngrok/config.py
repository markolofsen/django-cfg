"""
Main ngrok configuration for django_cfg.

Simplified flat structure - only essential fields.
Domain and schemes are auto-determined from api_url in config.
"""

import os
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class NgrokConfig(BaseModel):
    """Simplified flat ngrok configuration for django-cfg.

    Key simplifications:
    - No domain field (uses api_url from DjangoConfig automatically)
    - No schemes field (auto-determined from api_url: http:// -> http, https:// -> https)
    - Flat structure (no nested NgrokAuthConfig/NgrokTunnelConfig)
    """

    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True,
        "extra": "forbid"
    }

    # Control
    enabled: bool = Field(
        default=False,
        description="Enable ngrok integration (only works in DEBUG mode)"
    )

    # Authentication
    authtoken: Optional[str] = Field(
        default=None,
        description="Ngrok auth token. If None, will try NGROK_AUTHTOKEN env var",
        repr=False  # Don't show in repr for security
    )

    # Optional tunnel features
    basic_auth: Optional[List[str]] = Field(
        default=None,
        description="Basic auth credentials in format ['user:pass']"
    )

    compression: bool = Field(
        default=True,
        description="Enable gzip compression"
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

    def get_authtoken(self) -> Optional[str]:
        """Get auth token from config or environment."""
        if self.authtoken:
            return self.authtoken
        return os.environ.get("NGROK_AUTHTOKEN")


__all__ = [
    "NgrokConfig",
]
