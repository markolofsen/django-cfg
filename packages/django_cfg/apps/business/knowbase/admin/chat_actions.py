"""
Chat admin actions.
"""

from datetime import timedelta

from django.contrib import messages
from django.utils import timezone


def activate_sessions(modeladmin, request, queryset):
    """Activate selected sessions."""
    updated = queryset.update(is_active=True)
    messages.success(request, f"Activated {updated} sessions.")


def deactivate_sessions(modeladmin, request, queryset):
    """Deactivate selected sessions."""
    updated = queryset.update(is_active=False)
    messages.warning(request, f"Deactivated {updated} sessions.")


def clear_old_sessions(modeladmin, request, queryset):
    """Clear old inactive sessions."""
    cutoff_date = timezone.now() - timedelta(days=30)
    old_sessions = queryset.filter(is_active=False, last_activity_at__lt=cutoff_date)
    count = old_sessions.count()

    if count > 0:
        messages.warning(request, f"Clear old sessions functionality not implemented yet. {count} old sessions found.")
    else:
        messages.info(request, "No old sessions found to clear.")


def delete_user_messages(modeladmin, request, queryset):
    """Delete user messages from selection."""
    user_messages = queryset.filter(role='user')
    count = user_messages.count()

    if count > 0:
        messages.warning(request, f"Delete user messages functionality not implemented yet. {count} user messages selected.")
    else:
        messages.info(request, "No user messages in selection.")


def delete_assistant_messages(modeladmin, request, queryset):
    """Delete assistant messages from selection."""
    assistant_messages = queryset.filter(role='assistant')
    count = assistant_messages.count()

    if count > 0:
        messages.warning(request, f"Delete assistant messages functionality not implemented yet. {count} assistant messages selected.")
    else:
        messages.info(request, "No assistant messages in selection.")
