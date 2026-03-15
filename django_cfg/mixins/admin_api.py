"""
Admin API Mixin.

Common configuration for admin-only API endpoints.
"""
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication


class AdminAPIMixin:
    """
    Mixin for admin-only API endpoints.

    Provides:
    - JWT, Session, and Basic authentication
    - IsAdminUser permission requirement

    Usage:
        class MyViewSet(AdminAPIMixin, viewsets.ModelViewSet):
            queryset = MyModel.objects.all()
            serializer_class = MySerializer

    Authentication Methods:
        1. JWT Token (Bearer): For frontend SPA authentication
        2. Session: For Django admin integration
        3. Basic Auth: For testing and scripts

    All endpoints require admin user privileges.
    """

    authentication_classes = [
        JWTAuthentication,      # JWT tokens (Bearer)
        SessionAuthentication,  # Django session (for admin)
        BasicAuthentication,    # HTTP Basic (for testing)
    ]
    permission_classes = [IsAdminUser]
