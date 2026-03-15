"""
Public API CORS Middleware.

Handles CORS for public API endpoints BEFORE django-cors-headers middleware.
This allows truly public endpoints (like lead submission) to accept requests
from any origin while keeping the rest of the app secured.

IMPORTANT: This middleware MUST be placed BEFORE 'corsheaders.middleware.CorsMiddleware'
in MIDDLEWARE settings for it to work correctly.
"""

import re
from typing import Callable, List, Optional

from django.conf import settings
from django.http import HttpRequest, HttpResponse


class PublicAPICORSMiddleware:
    """
    Middleware that handles CORS for public API endpoints.

    Public API endpoints can be configured via:
    - PUBLIC_API_CORS_PATHS: List of path prefixes (e.g., ['/cfg/leads/', '/api/public/'])
    - PUBLIC_API_CORS_REGEX: Regex pattern for matching paths

    All matching paths will have open CORS (Access-Control-Allow-Origin: *).

    Example settings.py:
        PUBLIC_API_CORS_PATHS = [
            '/cfg/leads/',
            '/api/webhooks/',
        ]

    Or using regex:
        PUBLIC_API_CORS_REGEX = r'^/(cfg/leads|api/webhooks)/'

    Usage in MIDDLEWARE (must be BEFORE corsheaders):
        MIDDLEWARE = [
            'django_cfg.core.middleware.PublicAPICORSMiddleware',  # FIRST!
            'corsheaders.middleware.CorsMiddleware',
            ...
        ]
    """

    # Default CORS headers for public APIs
    CORS_HEADERS = {
        "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": (
            "Content-Type, Authorization, X-Requested-With, Accept, Origin, "
            "X-CSRFToken, X-Forwarded-For, User-Agent, Referer, "
            "sec-ch-ua, sec-ch-ua-mobile, sec-ch-ua-platform"
        ),
        "Access-Control-Max-Age": "86400",
    }

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

        # Get configuration from settings
        self.public_paths: List[str] = getattr(
            settings, "PUBLIC_API_CORS_PATHS", ["/cfg/leads/"]
        )
        self.public_regex: Optional[str] = getattr(
            settings, "PUBLIC_API_CORS_REGEX", None
        )

        # Compile regex if provided
        self._compiled_regex = None
        if self.public_regex:
            self._compiled_regex = re.compile(self.public_regex)

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process request and add CORS headers for public API paths."""

        # Check if this is a public API path
        if not self._is_public_api_path(request.path):
            return self.get_response(request)

        # Handle OPTIONS preflight request
        if request.method == "OPTIONS":
            response = HttpResponse(status=200)
            self._add_cors_headers(response, request)
            return response

        # Process request and add CORS headers to response
        response = self.get_response(request)
        self._add_cors_headers(response, request)

        return response

    def _is_public_api_path(self, path: str) -> bool:
        """
        Check if the request path is a public API endpoint.

        Args:
            path: Request path (e.g., '/cfg/leads/submit/')

        Returns:
            True if path matches public API configuration
        """
        # Check path prefixes
        for public_path in self.public_paths:
            if path.startswith(public_path):
                return True

        # Check regex pattern
        if self._compiled_regex and self._compiled_regex.match(path):
            return True

        return False

    def _add_cors_headers(self, response: HttpResponse, request: HttpRequest) -> None:
        """
        Add CORS headers to response.
        
        For public APIs we allow ANY origin without restrictions.
        Always echo back the Origin header if present, or use * as fallback.
        """
        # Get origin from request, default to * for universal access
        origin = request.META.get("HTTP_ORIGIN", "*")

        # Always allow the requesting origin
        response["Access-Control-Allow-Origin"] = origin
        response["Access-Control-Allow-Methods"] = self.CORS_HEADERS["Access-Control-Allow-Methods"]
        response["Access-Control-Allow-Headers"] = self.CORS_HEADERS["Access-Control-Allow-Headers"]
        response["Access-Control-Max-Age"] = self.CORS_HEADERS["Access-Control-Max-Age"]
        
        # Only set credentials when we have specific origin (not wildcard)
        # This is required by CORS spec: can't use credentials with '*'
        if origin != "*":
            response["Access-Control-Allow-Credentials"] = "true"
