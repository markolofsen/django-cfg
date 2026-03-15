"""
Public API Mixin.

Mixin for public API endpoints without authentication.
CORS is handled by PublicAPICORSMiddleware (configured via PUBLIC_API_CORS_PATHS).
"""

from typing import Any, List

from rest_framework.permissions import AllowAny


class PublicAPIMixin:
    """
    Mixin for public API endpoints.

    Provides:
    - AllowAny permission (no authentication required)
    - No authentication classes

    CORS is handled by PublicAPICORSMiddleware middleware.
    Configure paths in settings: PUBLIC_API_CORS_PATHS = ['/cfg/leads/']

    Usage:
        class LeadViewSet(PublicAPIMixin, viewsets.ModelViewSet):
            queryset = Lead.objects.all()
            serializer_class = LeadSerializer
    """

    permission_classes = [AllowAny]
    authentication_classes: List[Any] = []
