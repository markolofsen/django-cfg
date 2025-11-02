"""
SuperAdmin API Mixin.

Common configuration for superuser-only API endpoints.
More restrictive than AdminAPIMixin - requires is_superuser flag.
"""
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication


class IsSuperUser(BasePermission):
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


class SuperAdminAPIMixin:
    """
    Mixin for superuser-only API endpoints.

    Provides:
    - JWT, Session, and Basic authentication
    - IsSuperUser permission requirement (is_superuser=True)

    Usage:
        class MyViewSet(SuperAdminAPIMixin, viewsets.ModelViewSet):
            queryset = MyModel.objects.all()
            serializer_class = MySerializer

    Authentication Methods:
        1. JWT Token (Bearer): For frontend SPA authentication
        2. Session: For Django admin integration
        3. Basic Auth: For testing and scripts

    All endpoints require superuser privileges.
    Only use this for sensitive operations like:
    - Command execution
    - System configuration changes
    - Direct database operations
    """

    authentication_classes = [
        JWTAuthentication,      # JWT tokens (Bearer)
        SessionAuthentication,  # Django session (for admin)
        BasicAuthentication,    # HTTP Basic (for testing)
    ]
    permission_classes = [IsSuperUser]
