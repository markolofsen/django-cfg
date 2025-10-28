"""
Dashboard Permissions

Custom permission classes for dashboard API endpoints.
"""

from rest_framework.permissions import BasePermission


class IsSuperAdmin(BasePermission):
    """
    Permission that allows access only to superusers.

    More restrictive than IsAdminUser - requires is_superuser flag.
    Use for sensitive operations like command execution.
    """

    def has_permission(self, request, view):
        """Check if user is authenticated and is a superuser."""
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_superuser
        )


class IsStaffOrReadOnly(BasePermission):
    """
    Permission that allows read access to staff,
    but write access only to superusers.
    """

    def has_permission(self, request, view):
        """Check permissions based on request method."""
        # Read permissions are allowed to any staff user
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return bool(
                request.user and
                request.user.is_authenticated and
                request.user.is_staff
            )

        # Write permissions are only allowed to superusers
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_superuser
        )
