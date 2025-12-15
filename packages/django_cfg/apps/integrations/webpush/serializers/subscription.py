"""
Serializers for Web Push subscriptions.
"""

from rest_framework import serializers


class SubscribeRequestSerializer(serializers.Serializer):
    """Request serializer for subscribing to push notifications."""

    endpoint = serializers.URLField(
        max_length=500,
        help_text="Push service endpoint URL from browser"
    )
    keys = serializers.DictField(
        child=serializers.CharField(),
        help_text="Encryption keys (p256dh and auth)"
    )

    def validate_keys(self, value):
        """Validate that required keys are present."""
        required_keys = ['p256dh', 'auth']
        for key in required_keys:
            if key not in value:
                raise serializers.ValidationError(f"Missing required key: {key}")
        return value


class SubscribeResponseSerializer(serializers.Serializer):
    """Response serializer for subscription endpoint."""

    success = serializers.BooleanField(help_text="Whether subscription was successful")
    subscription_id = serializers.IntegerField(help_text="ID of the subscription")
    created = serializers.BooleanField(help_text="Whether subscription was newly created")


class SendPushRequestSerializer(serializers.Serializer):
    """Request serializer for sending push notifications."""

    title = serializers.CharField(
        max_length=255,
        help_text="Notification title"
    )
    body = serializers.CharField(
        help_text="Notification body"
    )
    icon = serializers.URLField(
        required=False,
        allow_null=True,
        help_text="Notification icon URL"
    )
    url = serializers.URLField(
        required=False,
        allow_null=True,
        help_text="URL to open on click"
    )


class SendPushResponseSerializer(serializers.Serializer):
    """Response serializer for send push endpoint."""

    success = serializers.BooleanField(help_text="Whether send was successful")
    sent_to = serializers.IntegerField(help_text="Number of devices notification was sent to")


class VapidPublicKeyResponseSerializer(serializers.Serializer):
    """Response serializer for VAPID public key endpoint."""

    publicKey = serializers.CharField(help_text="VAPID public key for client subscription")


__all__ = [
    "SubscribeRequestSerializer",
    "SubscribeResponseSerializer",
    "SendPushRequestSerializer",
    "SendPushResponseSerializer",
    "VapidPublicKeyResponseSerializer",
]
