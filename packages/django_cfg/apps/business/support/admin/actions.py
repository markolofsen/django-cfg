"""
Support admin actions.
"""

from django.contrib import messages


def mark_tickets_as_open(modeladmin, request, queryset):
    """Mark selected tickets as open."""
    count = queryset.update(status='open')
    messages.info(request, f"Marked {count} tickets as open.")


def mark_tickets_as_waiting_for_user(modeladmin, request, queryset):
    """Mark selected tickets as waiting for user."""
    count = queryset.update(status='waiting_for_user')
    messages.warning(request, f"Marked {count} tickets as waiting for user.")


def mark_tickets_as_waiting_for_admin(modeladmin, request, queryset):
    """Mark selected tickets as waiting for admin."""
    count = queryset.update(status='waiting_for_admin')
    messages.info(request, f"Marked {count} tickets as waiting for admin.")


def mark_tickets_as_resolved(modeladmin, request, queryset):
    """Mark selected tickets as resolved."""
    count = queryset.update(status='resolved')
    messages.success(request, f"Marked {count} tickets as resolved.")


def mark_tickets_as_closed(modeladmin, request, queryset):
    """Mark selected tickets as closed."""
    count = queryset.update(status='closed')
    messages.error(request, f"Marked {count} tickets as closed.")
