"""
Archive admin actions.
"""

from django.contrib import messages


def reprocess_archives(modeladmin, request, queryset):
    """Reprocess selected archives."""
    count = queryset.count()
    messages.info(request, f"Reprocess functionality not implemented yet. {count} archives selected.")


def mark_as_public(modeladmin, request, queryset):
    """Mark selected archives as public."""
    updated = queryset.update(is_public=True)
    messages.success(request, f"Marked {updated} archives as public.")


def mark_as_private(modeladmin, request, queryset):
    """Mark selected archives as private."""
    updated = queryset.update(is_public=False)
    messages.warning(request, f"Marked {updated} archives as private.")


def mark_as_processable(modeladmin, request, queryset):
    """Mark selected items as processable."""
    updated = queryset.update(is_processable=True)
    messages.success(request, f"Marked {updated} items as processable.")


def mark_as_not_processable(modeladmin, request, queryset):
    """Mark selected items as not processable."""
    updated = queryset.update(is_processable=False)
    messages.warning(request, f"Marked {updated} items as not processable.")


def regenerate_embeddings(modeladmin, request, queryset):
    """Regenerate embeddings for selected chunks."""
    count = queryset.count()
    messages.info(request, f"Regenerate embeddings functionality not implemented yet. {count} chunks selected.")


def clear_embeddings(modeladmin, request, queryset):
    """Clear embeddings for selected chunks."""
    updated = queryset.update(embedding=None)
    messages.warning(request, f"Cleared embeddings for {updated} chunks.")
