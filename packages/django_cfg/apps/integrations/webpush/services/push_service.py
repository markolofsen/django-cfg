"""
Web Push notification service.

Type-safe async push notification service following CRITICAL_REQUIREMENTS.md.

Main functions:
- send_push(user, payload) - Send to one user
- send_push_to_many(user_ids, payload) - Send to multiple users
"""

from typing import TYPE_CHECKING, List, Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django_cfg.utils import get_logger
from pywebpush import WebPushException, webpush

from .exceptions import (
    WebPushConfigurationError,
    WebPushDeliveryError,
    WebPushSubscriptionError,
)
from .models import BulkPushResult, PushPayload, PushResult, VapidConfig

if TYPE_CHECKING:
    from ..models import PushSubscription

logger = get_logger("webpush")


async def _get_vapid_config() -> VapidConfig:
    """
    Get VAPID configuration from settings.

    Returns:
        VapidConfig: Validated VAPID configuration

    Raises:
        WebPushConfigurationError: If VAPID keys are not configured
    """
    private_key = getattr(settings, "WEBPUSH__VAPID_PRIVATE_KEY", None)
    public_key = getattr(settings, "WEBPUSH__VAPID_PUBLIC_KEY", None)
    mailto = getattr(
        settings, "WEBPUSH__VAPID_MAILTO", "mailto:noreply@djangocfg.com"
    )

    if not private_key or not public_key:
        raise WebPushConfigurationError(
            message="VAPID keys not configured",
            details={
                "has_private_key": bool(private_key),
                "has_public_key": bool(public_key),
            },
        )

    return VapidConfig(
        private_key=private_key,
        public_key=public_key,
        mailto=mailto,
    )


async def _send_to_subscription(
    subscription: "PushSubscription",
    payload: PushPayload,
    vapid_config: VapidConfig,
) -> bool:
    """
    Send push notification to a single subscription.

    Args:
        subscription: Push subscription model
        payload: Notification payload
        vapid_config: VAPID configuration

    Returns:
        bool: True if sent successfully, False otherwise

    Raises:
        WebPushDeliveryError: If delivery fails critically
    """
    try:
        # Convert payload to JSON string
        payload_json = payload.model_dump_json()

        # Convert subscription to pywebpush format
        subscription_info = subscription.to_webpush_dict()

        # Prepare VAPID claims
        vapid_claims = {"sub": vapid_config.mailto}

        # Send notification
        webpush(
            subscription_info=subscription_info,
            data=payload_json,
            vapid_private_key=vapid_config.private_key,
            vapid_claims=vapid_claims,
        )

        logger.info(
            f"Push sent to user {subscription.user_id}, "
            f"endpoint: {subscription.endpoint[:50]}..."
        )
        return True

    except WebPushException as e:
        logger.warning(
            f"Push failed for subscription {subscription.id}: {e}",
            exc_info=True,
        )

        # Deactivate expired subscriptions (410 Gone, 404 Not Found)
        if (
            hasattr(e, "response")
            and e.response
            and e.response.status_code in [404, 410]
        ):
            subscription.is_active = False
            await subscription.asave()
            logger.info(f"Deactivated expired subscription {subscription.id}")

        return False

    except Exception as e:
        logger.error(
            f"Unexpected error sending push to subscription {subscription.id}: {e}",
            exc_info=True,
        )
        raise WebPushDeliveryError(
            message="Failed to send push notification",
            details={
                "subscription_id": subscription.id,
                "error": str(e),
            },
        ) from e


async def send_push(
    user,  # Type: User (from AUTH_USER_MODEL)
    title: str,
    body: str,
    icon: Optional[str] = None,
    url: Optional[str] = None,
) -> int:
    """
    Send push notification to all active subscriptions for a user.

    Args:
        user: Django User instance
        title: Notification title
        body: Notification body
        icon: Icon URL (optional)
        url: URL to open on click (optional)

    Returns:
        int: Number of successfully sent notifications

    Raises:
        WebPushConfigurationError: If VAPID keys not configured
        WebPushSubscriptionError: If no active subscriptions found

    Example:
        >>> from django_cfg.apps.integrations.webpush import send_push
        >>> sent = await send_push(
        ...     user=request.user,
        ...     title="Hello",
        ...     body="Test notification"
        ... )
        >>> print(f"Sent to {sent} devices")
    """
    # Lazy import to avoid AppRegistryNotReady
    from ..models import PushSubscription

    # Get VAPID configuration
    vapid_config = await _get_vapid_config()

    # Create validated payload
    payload = PushPayload(
        title=title,
        body=body,
        icon=icon if icon else None,
        url=url if url else None,
    )

    # Get active subscriptions for user (async iteration)
    subscriptions = [
        s async for s in PushSubscription.objects.filter(user=user, is_active=True)
    ]

    if not subscriptions:
        logger.warning(f"No active subscriptions for user {user.id}")
        raise WebPushSubscriptionError(
            message="No active push subscriptions found",
            details={"user_id": user.id},
        )

    # Send to each subscription
    success_count = 0
    for subscription in subscriptions:
        try:
            success = await _send_to_subscription(subscription, payload, vapid_config)
            if success:
                success_count += 1
        except WebPushDeliveryError:
            # Continue to next subscription on critical error
            continue

    return success_count


async def send_push_to_many(
    user_ids: List[int],
    title: str,
    body: str,
    icon: Optional[str] = None,
    url: Optional[str] = None,
) -> BulkPushResult:
    """
    Send push notification to multiple users.

    Args:
        user_ids: List of user IDs
        title: Notification title
        body: Notification body
        icon: Icon URL (optional)
        url: URL to open on click (optional)

    Returns:
        BulkPushResult: Statistics with Pydantic model

    Raises:
        WebPushConfigurationError: If VAPID keys not configured

    Example:
        >>> from django_cfg.apps.integrations.webpush import send_push_to_many
        >>> result = await send_push_to_many(
        ...     user_ids=[1, 2, 3],
        ...     title="Announcement",
        ...     body="Important update"
        ... )
        >>> print(f"Sent to {result.sent} devices")
    """
    User = get_user_model()
    users = [u async for u in User.objects.filter(id__in=user_ids)]

    total_sent = 0
    total_failed = 0

    for user in users:
        try:
            count = await send_push(user, title, body, icon, url)
            total_sent += count
        except WebPushSubscriptionError:
            # User has no subscriptions
            total_failed += 1
            logger.debug(f"No subscriptions for user {user.id}")
        except WebPushConfigurationError as e:
            # Configuration error - stop processing
            logger.error(f"VAPID configuration error: {e}")
            raise

    return BulkPushResult(
        success=True,
        sent=total_sent,
        failed=total_failed,
        total_users=len(users),
    )


__all__ = ["send_push", "send_push_to_many"]
