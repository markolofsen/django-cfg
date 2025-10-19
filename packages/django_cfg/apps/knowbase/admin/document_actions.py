"""
Document admin actions.
"""

from django.contrib import messages


def reprocess_documents(modeladmin, request, queryset):
    """Reprocess selected documents."""
    count = queryset.count()
    messages.info(request, f"Reprocessing functionality not implemented yet. {count} documents selected.")


def mark_as_public(modeladmin, request, queryset):
    """Mark selected items as public."""
    updated = queryset.update(is_public=True)
    messages.success(request, f"Marked {updated} item(s) as public.")


def mark_as_private(modeladmin, request, queryset):
    """Mark selected items as private."""
    updated = queryset.update(is_public=False)
    messages.warning(request, f"Marked {updated} item(s) as private.")


def regenerate_embeddings(modeladmin, request, queryset):
    """Regenerate embeddings for selected chunks."""
    count = queryset.count()
    messages.info(request, f"Regenerate embeddings functionality not implemented yet. {count} chunks selected.")


def clear_embeddings(modeladmin, request, queryset):
    """Clear embeddings for selected chunks."""
    updated = queryset.update(embedding=None)
    messages.warning(request, f"Cleared embeddings for {updated} chunks.")


def make_public(modeladmin, request, queryset):
    """Mark selected categories as public."""
    updated = queryset.update(is_public=True)
    messages.success(request, f"Marked {updated} item(s) as public.")


def make_private(modeladmin, request, queryset):
    """Mark selected categories as private."""
    updated = queryset.update(is_public=False)
    messages.warning(request, f"Marked {updated} item(s) as private.")
