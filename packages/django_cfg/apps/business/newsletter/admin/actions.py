"""
Newsletter admin actions.

Standalone action handlers for Newsletter, NewsletterSubscription, and NewsletterCampaign admins.
"""

from django.contrib import messages
from django.db.models import QuerySet

from ..models import Newsletter, NewsletterCampaign, NewsletterSubscription

# ===== Newsletter Actions =====

def activate_newsletters(modeladmin, request, queryset: QuerySet[Newsletter]):
    """Activate selected newsletters."""
    count = queryset.update(is_active=True)
    modeladmin.message_user(
        request,
        f"Successfully activated {count} newsletter(s).",
        level=messages.SUCCESS
    )


def deactivate_newsletters(modeladmin, request, queryset: QuerySet[Newsletter]):
    """Deactivate selected newsletters."""
    count = queryset.update(is_active=False)
    modeladmin.message_user(
        request,
        f"Successfully deactivated {count} newsletter(s).",
        level=messages.WARNING
    )


def enable_auto_subscribe(modeladmin, request, queryset: QuerySet[Newsletter]):
    """Enable auto subscribe for selected newsletters."""
    count = queryset.update(auto_subscribe=True)
    modeladmin.message_user(
        request,
        f"Enabled auto subscribe for {count} newsletter(s).",
        level=messages.INFO
    )


# ===== NewsletterSubscription Actions =====

def activate_subscriptions(modeladmin, request, queryset: QuerySet[NewsletterSubscription]):
    """Activate selected subscriptions."""
    count = queryset.update(is_active=True)
    modeladmin.message_user(
        request,
        f"Successfully activated {count} subscription(s).",
        level=messages.SUCCESS
    )


def deactivate_subscriptions(modeladmin, request, queryset: QuerySet[NewsletterSubscription]):
    """Deactivate selected subscriptions."""
    count = queryset.update(is_active=False)
    modeladmin.message_user(
        request,
        f"Successfully deactivated {count} subscription(s).",
        level=messages.WARNING
    )


# ===== NewsletterCampaign Actions =====

def send_campaigns(modeladmin, request, queryset: QuerySet[NewsletterCampaign]):
    """Send selected campaigns."""
    sendable_count = queryset.filter(status__in=['draft', 'scheduled']).count()
    if sendable_count == 0:
        modeladmin.message_user(
            request,
            "No sendable campaigns selected.",
            level=messages.ERROR
        )
        return

    queryset.filter(status__in=['draft', 'scheduled']).update(status='sending')
    modeladmin.message_user(
        request,
        f"Started sending {sendable_count} campaign(s).",
        level=messages.SUCCESS
    )


def schedule_campaigns(modeladmin, request, queryset: QuerySet[NewsletterCampaign]):
    """Schedule selected campaigns."""
    schedulable_count = queryset.filter(status='draft').count()
    if schedulable_count == 0:
        modeladmin.message_user(
            request,
            "No draft campaigns selected.",
            level=messages.ERROR
        )
        return

    queryset.filter(status='draft').update(status='scheduled')
    modeladmin.message_user(
        request,
        f"Scheduled {schedulable_count} campaign(s).",
        level=messages.WARNING
    )


def cancel_campaigns(modeladmin, request, queryset: QuerySet[NewsletterCampaign]):
    """Cancel selected campaigns."""
    cancelable_count = queryset.filter(status__in=['draft', 'scheduled']).count()
    if cancelable_count == 0:
        modeladmin.message_user(
            request,
            "No cancelable campaigns selected.",
            level=messages.ERROR
        )
        return

    queryset.filter(status__in=['draft', 'scheduled']).update(status='cancelled')
    modeladmin.message_user(
        request,
        f"Cancelled {cancelable_count} campaign(s).",
        level=messages.ERROR
    )
