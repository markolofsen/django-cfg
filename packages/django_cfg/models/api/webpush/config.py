"""
Web Push Configuration Models.

Type-safe configuration for Web Push notifications using Pydantic v2.
"""

from typing import Annotated, Optional

from pydantic import BaseModel, Field


class WebPushConfig(BaseModel):
    """
    Web Push notification configuration.

    Configuration for VAPID-based push notifications following RFC 8030.

    Example:
        ```python
        from django_cfg import DjangoConfig
        from django_cfg.models.api.webpush import WebPushConfig

        class MyConfig(DjangoConfig):
            webpush: WebPushConfig = WebPushConfig(
                enabled=True,
                vapid_private_key="${WEBPUSH__VAPID_PRIVATE_KEY}",
                vapid_public_key="${WEBPUSH__VAPID_PUBLIC_KEY}",
                vapid_mailto="mailto:admin@example.com",
            )
        ```
    """

    enabled: bool = Field(
        default=False,
        description="Enable Web Push notifications integration",
    )

    vapid_private_key: Optional[str] = Field(
        default=None,
        description="VAPID private key for authentication (generate with: npx web-push generate-vapid-keys)",
    )

    vapid_public_key: Optional[str] = Field(
        default=None,
        description="VAPID public key for client subscription",
    )

    vapid_mailto: str = Field(
        default="mailto:noreply@djangocfg.com",
        description="VAPID mailto claim (RFC 8292)",
    )

    def get_settings_dict(self) -> dict:
        """
        Convert to Django settings dictionary.

        Returns:
            Dictionary with WEBPUSH__ prefixed settings
        """
        return {
            "WEBPUSH__ENABLED": self.enabled,
            "WEBPUSH__VAPID_PRIVATE_KEY": self.vapid_private_key,
            "WEBPUSH__VAPID_PUBLIC_KEY": self.vapid_public_key,
            "WEBPUSH__VAPID_MAILTO": self.vapid_mailto,
        }


__all__ = ["WebPushConfig"]
