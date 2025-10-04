"""
Shared admin actions for visibility management.

Provides consistent actions for toggling public/private status across
all knowbase admin interfaces.
"""

from django.contrib import messages
from django_cfg.modules.django_admin import action, ActionVariant


class VisibilityActions:
    """Shared actions for visibility management."""

    @staticmethod
    @action(description="Mark as public", variant=ActionVariant.SUCCESS)
    def mark_as_public(modeladmin, request, queryset):
        """
        Mark selected items as public.

        Args:
            modeladmin: Admin class instance
            request: HTTP request object
            queryset: Selected items queryset

        Returns:
            None (displays success message)
        """
        updated = queryset.update(is_public=True)
        messages.success(request, f"Marked {updated} item(s) as public.")

    @staticmethod
    @action(description="Mark as private", variant=ActionVariant.WARNING)
    def mark_as_private(modeladmin, request, queryset):
        """
        Mark selected items as private.

        Args:
            modeladmin: Admin class instance
            request: HTTP request object
            queryset: Selected items queryset

        Returns:
            None (displays warning message)
        """
        updated = queryset.update(is_public=False)
        messages.warning(request, f"Marked {updated} item(s) as private.")


# Aliases for backward compatibility and consistency
# DocumentAdmin uses "mark_as_*" while DocumentCategoryAdmin used "make_*"
# These aliases ensure both naming conventions work
mark_as_public = VisibilityActions.mark_as_public
mark_as_private = VisibilityActions.mark_as_private
make_public = VisibilityActions.mark_as_public
make_private = VisibilityActions.mark_as_private
