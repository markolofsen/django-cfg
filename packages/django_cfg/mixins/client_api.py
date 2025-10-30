"""
Client API Mixin.

Common configuration for client API endpoints (authenticated users).
"""
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


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
        JWTAuthentication,      # JWT tokens (Bearer)
        SessionAuthentication,  # Django session
    ]
    permission_classes = [IsAuthenticated]
