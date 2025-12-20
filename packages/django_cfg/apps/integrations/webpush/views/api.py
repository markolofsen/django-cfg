"""
Web Push API ViewSet.

Provides REST API endpoints for Web Push notifications.

Note: Standard DRF ViewSets don't support async views. Options:
1. Use sync methods with sync ORM (current approach)
2. Use 'adrf' package: from adrf.viewsets import ViewSet as AsyncViewSet
For async push sending, use the async service directly.
"""

from asgiref.sync import async_to_sync
from django.conf import settings
from django_cfg.utils import get_logger
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import PushSubscription
from ..serializers import (
    SendPushRequestSerializer,
    SendPushResponseSerializer,
    SubscribeRequestSerializer,
    SubscribeResponseSerializer,
    VapidPublicKeyResponseSerializer,
)
from ..services.push_service import send_push

logger = get_logger("webpush.api")


class WebPushViewSet(viewsets.GenericViewSet):
    """
    ViewSet for Web Push notifications.

    Provides endpoints for:
    - Subscribing to push notifications
    - Sending push notifications
    - Getting VAPID public key
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Web Push"],
        summary="Subscribe to push notifications",
        description="Save push subscription from browser for the authenticated user.",
        request=SubscribeRequestSerializer,
        responses={
            200: SubscribeResponseSerializer,
            400: {"description": "Bad request"},
        },
    )
    @action(detail=False, methods=["post"], url_path="subscribe")
    def subscribe(self, request):
        """Save push subscription for authenticated user."""
        serializer = SubscribeRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        endpoint = data["endpoint"]
        keys = data["keys"]

        try:
            # Update or create subscription (sync ORM)
            subscription, created = PushSubscription.objects.update_or_create(
                endpoint=endpoint,
                defaults={
                    "user": request.user,
                    "p256dh": keys["p256dh"],
                    "auth": keys["auth"],
                    "is_active": True,
                },
            )

            response_serializer = SubscribeResponseSerializer(
                {
                    "success": True,
                    "subscription_id": subscription.id,
                    "created": created,
                }
            )

            logger.info(
                f"Subscription {'created' if created else 'updated'} for user {request.user.id}"
            )

            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error saving subscription: {e}", exc_info=True)
            return Response(
                {"error": "Failed to save subscription"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["Web Push"],
        summary="Send push notification",
        description="Send push notification to all active subscriptions for the authenticated user.",
        request=SendPushRequestSerializer,
        responses={
            200: SendPushResponseSerializer,
            400: {"description": "Bad request"},
        },
    )
    @action(detail=False, methods=["post"], url_path="send")
    def send_notification(self, request):
        """Send push notification to authenticated user's devices."""
        serializer = SendPushRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        try:
            # Use async_to_sync wrapper for async send_push function
            count = async_to_sync(send_push)(
                user=request.user,
                title=data["title"],
                body=data["body"],
                icon=data.get("icon"),
                url=data.get("url"),
            )

            response_serializer = SendPushResponseSerializer(
                {"success": True, "sent_to": count}
            )

            logger.info(f"Push sent to {count} device(s) for user {request.user.id}")

            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error sending push: {e}", exc_info=True)
            return Response(
                {"error": "Failed to send push notification"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["Web Push"],
        summary="Get VAPID public key",
        description="Get VAPID public key for client subscription.",
        responses={
            200: VapidPublicKeyResponseSerializer,
            503: {"description": "Service unavailable"},
        },
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="vapid",
        permission_classes=[],  # Public endpoint
    )
    def vapid_public_key(self, request):
        """Get VAPID public key for client subscription."""
        public_key = getattr(settings, "WEBPUSH__VAPID_PUBLIC_KEY", None)

        if not public_key:
            logger.error("VAPID public key not configured")
            return Response(
                {"error": "VAPID public key not configured"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        response_serializer = VapidPublicKeyResponseSerializer({"publicKey": public_key})

        return Response(response_serializer.data, status=status.HTTP_200_OK)


__all__ = ["WebPushViewSet"]
