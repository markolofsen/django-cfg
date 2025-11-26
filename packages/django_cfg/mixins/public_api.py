"""
Public API Mixin.

Common configuration for public API endpoints with open CORS.
"""
from typing import Any, List, Optional

from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response


class PublicAPIMixin:
    """
    Mixin for public API endpoints with open CORS.

    Provides:
    - AllowAny permission (no authentication required)
    - CORS headers for cross-origin requests
    - OPTIONS preflight handling

    Usage:
        class LeadViewSet(PublicAPIMixin, viewsets.ModelViewSet):
            queryset = Lead.objects.all()
            serializer_class = LeadSerializer

        # Or for specific actions only:
        class MyViewSet(viewsets.ModelViewSet):
            @action(detail=False, methods=['post'])
            def submit(self, request):
                # Use PublicAPIResponse for CORS headers
                return PublicAPIResponse({'success': True})

    CORS Configuration:
        - Allow-Origin: * (all origins)
        - Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
        - Allow-Headers: Content-Type, Authorization, X-Requested-With
        - Max-Age: 86400 (24 hours cache for preflight)
    """

    permission_classes = [AllowAny]
    authentication_classes: List[Any] = []  # No authentication

    # CORS configuration
    cors_allow_origin: str = "*"
    cors_allow_methods: str = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    cors_allow_headers: str = "Content-Type, Authorization, X-Requested-With, Accept, Origin"
    cors_max_age: int = 86400  # 24 hours

    def finalize_response(
        self,
        request: Request,
        response: Response,
        *args: Any,
        **kwargs: Any
    ) -> Response:
        """Add CORS headers to response."""
        response = super().finalize_response(request, response, *args, **kwargs)
        self._add_cors_headers(response)
        return response

    def _add_cors_headers(self, response: Response) -> None:
        """Add CORS headers to the response."""
        response["Access-Control-Allow-Origin"] = self.cors_allow_origin
        response["Access-Control-Allow-Methods"] = self.cors_allow_methods
        response["Access-Control-Allow-Headers"] = self.cors_allow_headers
        response["Access-Control-Max-Age"] = str(self.cors_max_age)

    def options(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Handle OPTIONS preflight requests."""
        response = Response(status=200)
        self._add_cors_headers(response)
        return response


class PublicAPICORSMixin:
    """
    Lightweight mixin that only adds CORS headers (keeps existing auth).

    Use when you need CORS but want to keep authentication.

    Usage:
        class MyViewSet(PublicAPICORSMixin, AdminAPIMixin, viewsets.ModelViewSet):
            # Has admin auth BUT allows CORS
            pass
    """

    cors_allow_origin: str = "*"
    cors_allow_methods: str = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    cors_allow_headers: str = "Content-Type, Authorization, X-Requested-With, Accept, Origin"
    cors_max_age: int = 86400

    def finalize_response(
        self,
        request: Request,
        response: Response,
        *args: Any,
        **kwargs: Any
    ) -> Response:
        """Add CORS headers to response."""
        response = super().finalize_response(request, response, *args, **kwargs)
        response["Access-Control-Allow-Origin"] = self.cors_allow_origin
        response["Access-Control-Allow-Methods"] = self.cors_allow_methods
        response["Access-Control-Allow-Headers"] = self.cors_allow_headers
        response["Access-Control-Max-Age"] = str(self.cors_max_age)
        return response


class RestrictedCORSMixin:
    """
    Mixin with configurable CORS origins.

    Use when you need CORS but only from specific origins.

    Usage:
        class MyViewSet(RestrictedCORSMixin, viewsets.ModelViewSet):
            cors_allowed_origins = [
                "https://myapp.com",
                "https://admin.myapp.com",
            ]
    """

    cors_allowed_origins: List[str] = []
    cors_allow_methods: str = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    cors_allow_headers: str = "Content-Type, Authorization, X-Requested-With, Accept, Origin"
    cors_max_age: int = 86400

    def finalize_response(
        self,
        request: Request,
        response: Response,
        *args: Any,
        **kwargs: Any
    ) -> Response:
        """Add CORS headers if origin is allowed."""
        response = super().finalize_response(request, response, *args, **kwargs)

        origin = request.META.get("HTTP_ORIGIN", "")

        # Check if origin is allowed
        if origin and (not self.cors_allowed_origins or origin in self.cors_allowed_origins):
            response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Methods"] = self.cors_allow_methods
            response["Access-Control-Allow-Headers"] = self.cors_allow_headers
            response["Access-Control-Max-Age"] = str(self.cors_max_age)
            response["Access-Control-Allow-Credentials"] = "true"

        return response
