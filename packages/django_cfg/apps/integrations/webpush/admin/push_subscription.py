"""
Push Subscription Admin.

PydanticAdmin for PushSubscription model with custom computed fields.
"""

from django.contrib import admin
from django_cfg.modules.django_admin import Icons, computed_field
from django_cfg.modules.django_admin.base import PydanticAdmin

from ..models import PushSubscription
from .config import pushsubscription_config


@admin.register(PushSubscription)
class PushSubscriptionAdmin(PydanticAdmin):
    """
    Push subscription admin with testing actions.

    Features:
    - Status badge display
    - Test notification action
    - Endpoint display (shortened)
    """

    config = pushsubscription_config

    @computed_field("Endpoint", ordering="endpoint")
    def endpoint_short(self, obj):
        """Display shortened endpoint URL."""
        if len(obj.endpoint) > 50:
            return self.html.text(obj.endpoint[:47] + "...", variant="secondary")
        return self.html.text(obj.endpoint, variant="secondary")

    @computed_field("Status", ordering="is_active")
    def status_badge(self, obj):
        """Display status badge."""
        if obj.is_active:
            return self.html.badge("Active", variant="success", icon=Icons.CHECK_CIRCLE)
        else:
            return self.html.badge("Inactive", variant="danger", icon=Icons.ERROR)

    # Fieldsets for detail view
    def get_fieldsets(self, request, obj=None):
        """Dynamic fieldsets."""
        fieldsets = [
            (
                "Subscription Information",
                {"fields": ("id", "user", "endpoint", "is_active")},
            ),
            (
                "Encryption Keys",
                {
                    "fields": ("p256dh", "auth"),
                    "classes": ("collapse",),
                    "description": "VAPID encryption keys for push notifications",
                },
            ),
            (
                "Timestamps",
                {"fields": ("created_at", "updated_at")},
            ),
        ]

        return fieldsets

    # Admin actions
    actions = ["send_test_notification", "deactivate_subscriptions"]

    @admin.action(description="Send test notification")
    def send_test_notification(self, request, queryset):
        """Send test notification to selected subscriptions."""
        import asyncio
        from ..services.push_service import send_push

        # Get unique users from selected subscriptions
        user_ids = queryset.values_list("user_id", flat=True).distinct()

        async def send_to_users():
            from django.contrib.auth import get_user_model

            User = get_user_model()
            users = await User.objects.filter(id__in=user_ids).all()

            total_sent = 0
            for user in users:
                count = await send_push(
                    user,
                    title="Test Notification",
                    body="This is a test notification from Django Admin",
                    icon="/static/icon.png",
                    url="/",
                )
                total_sent += count

            return total_sent

        try:
            total_sent = asyncio.run(send_to_users())
            self.message_user(
                request, f"Test notification sent to {total_sent} device(s)", level="success"
            )
        except Exception as e:
            self.message_user(request, f"Error sending notification: {e}", level="error")

    @admin.action(description="Deactivate subscriptions")
    def deactivate_subscriptions(self, request, queryset):
        """Deactivate selected subscriptions."""
        count = queryset.update(is_active=False)
        self.message_user(
            request, f"Deactivated {count} subscription(s)", level="success"
        )


__all__ = ["PushSubscriptionAdmin"]
