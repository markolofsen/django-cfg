"""
Pydantic models for Web Push service.

Type-safe models following CRITICAL_REQUIREMENTS.md standards.
"""

from typing import Annotated, Optional

from pydantic import BaseModel, Field, HttpUrl


class PushPayload(BaseModel):
    """
    Push notification payload.

    Validated data structure for push notification content.
    """

    title: Annotated[str, Field(min_length=1, max_length=255)]
    body: Annotated[str, Field(min_length=1)]
    icon: Optional[HttpUrl] = Field(
        default="/icon.png", description="Notification icon URL"
    )
    url: Optional[HttpUrl] = Field(default="/", description="URL to open on click")


class VapidConfig(BaseModel):
    """
    VAPID configuration.

    Validated VAPID keys and claims.
    """

    private_key: Annotated[str, Field(min_length=1)]
    public_key: Annotated[str, Field(min_length=1)]
    mailto: str = Field(default="mailto:noreply@djangocfg.com")


class PushResult(BaseModel):
    """
    Result of send_push operation.

    Statistics for single user push notification.
    """

    success: bool
    sent_to_devices: int = Field(ge=0, description="Number of devices notified")
    failed_devices: int = Field(default=0, ge=0, description="Number of failed sends")


class BulkPushResult(BaseModel):
    """
    Result of send_push_to_many operation.

    Statistics for bulk push notification.
    """

    success: bool
    sent: int = Field(ge=0, description="Total devices notified")
    failed: int = Field(ge=0, description="Users with no subscriptions")
    total_users: int = Field(ge=0, description="Total users processed")


__all__ = ["PushPayload", "VapidConfig", "PushResult", "BulkPushResult"]
