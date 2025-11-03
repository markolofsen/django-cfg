"""
External Data admin actions.
"""

from django.contrib import messages


def reprocess_data(modeladmin, request, queryset):
    """Reprocess selected external data."""
    count = queryset.count()
    messages.info(request, f"Reprocess functionality not implemented yet. {count} items selected.")


def activate_data(modeladmin, request, queryset):
    """Activate selected external data."""
    updated = queryset.update(is_active=True)
    messages.success(request, f"Activated {updated} external data items.")


def deactivate_data(modeladmin, request, queryset):
    """Deactivate selected external data."""
    updated = queryset.update(is_active=False)
    messages.warning(request, f"Deactivated {updated} external data items.")


def mark_as_public(modeladmin, request, queryset):
    """Mark selected data as public."""
    updated = queryset.update(is_public=True)
    messages.success(request, f"Marked {updated} items as public.")


def mark_as_private(modeladmin, request, queryset):
    """Mark selected data as private."""
    updated = queryset.update(is_public=False)
    messages.warning(request, f"Marked {updated} items as private.")


def regenerate_embeddings(modeladmin, request, queryset):
    """Regenerate embeddings for selected chunks."""
    count = queryset.count()
    messages.info(request, f"Regenerate embeddings functionality not implemented yet. {count} chunks selected.")


def clear_embeddings(modeladmin, request, queryset):
    """Clear embeddings for selected chunks."""
    updated = queryset.update(embedding=None)
    messages.warning(request, f"Cleared embeddings for {updated} chunks.")
