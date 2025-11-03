"""
Lead admin actions.
"""

from django.contrib import messages


def mark_as_contacted(modeladmin, request, queryset):
    """Mark selected leads as contacted."""
    updated = queryset.update(status='contacted')
    messages.warning(request, f"Marked {updated} leads as contacted.")


def mark_as_qualified(modeladmin, request, queryset):
    """Mark selected leads as qualified."""
    updated = queryset.update(status='qualified')
    messages.info(request, f"Marked {updated} leads as qualified.")


def mark_as_converted(modeladmin, request, queryset):
    """Mark selected leads as converted."""
    updated = queryset.update(status='converted')
    messages.success(request, f"Marked {updated} leads as converted.")


def mark_as_rejected(modeladmin, request, queryset):
    """Mark selected leads as rejected."""
    updated = queryset.update(status='rejected')
    messages.error(request, f"Marked {updated} leads as rejected.")
