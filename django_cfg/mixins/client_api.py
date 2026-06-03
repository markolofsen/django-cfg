"""
Client API Mixin.

Common configuration for client API endpoints (authenticated users).
"""
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated

# Use django_cfg's JWT auth (NOT stock simplejwt JWTAuthentication): it adds
# last-login tracking, is_active checks, AND DPoP (RFC 9449) proof enforcement.
# Hardcoding stock JWTAuthentication here silently bypassed DPoP for every
# ClientAPIMixin endpoint.
from django_cfg.middleware.authentication import JWTAuthenticationWithLastLogin


class ClientAPIMixin:
    """
    Mixin for client API endpoints (authenticated regular users).

    Provides:
    - JWT and Session authentication
    - IsAuthenticated permission requirement

    Usage:
        class MyViewSet(ClientAPIMixin, viewsets.ModelViewSet):
            queryset = MyModel.objects.all()
            serializer_class = MySerializer

            def get_queryset(self):
                # Filter by current user
                return super().get_queryset().filter(user=self.request.user)

    Authentication Methods:
        1. JWT Token (Bearer): For frontend SPA authentication
        2. Session: For web browser sessions

    All endpoints require authenticated user (not necessarily admin).
    """

    authentication_classes = [
        JWTAuthenticationWithLastLogin,  # JWT (Bearer) + DPoP enforcement
        SessionAuthentication,           # Django session
    ]
    permission_classes = [IsAuthenticated]
