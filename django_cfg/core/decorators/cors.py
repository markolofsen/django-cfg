"""
CORS Decorators.

Decorators for adding CORS headers to views and API endpoints.
Works with both function-based and class-based views.
"""
from functools import wraps
from typing import Callable, List, Optional, TypeVar, Union

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

F = TypeVar("F", bound=Callable)

# Default CORS headers
DEFAULT_CORS_METHODS = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
DEFAULT_CORS_HEADERS = "Content-Type, Authorization, X-Requested-With, Accept, Origin"
DEFAULT_CORS_MAX_AGE = 86400  # 24 hours


def _add_cors_headers(
    response: HttpResponse,
    origin: str = "*",
    methods: str = DEFAULT_CORS_METHODS,
    headers: str = DEFAULT_CORS_HEADERS,
    max_age: int = DEFAULT_CORS_MAX_AGE,
    credentials: bool = False,
) -> HttpResponse:
    """Add CORS headers to response."""
    response["Access-Control-Allow-Origin"] = origin
    response["Access-Control-Allow-Methods"] = methods
    response["Access-Control-Allow-Headers"] = headers
    response["Access-Control-Max-Age"] = str(max_age)
    if credentials:
        response["Access-Control-Allow-Credentials"] = "true"
    return response


def cors_allow_all(view_func: F) -> F:
    """
    Decorator to allow CORS from any origin.

    Adds CORS headers and disables CSRF for the view.
    Handles OPTIONS preflight requests automatically.

    Usage:
        @cors_allow_all
        def my_view(request):
            return JsonResponse({'success': True})

        # With DRF api_view
        @cors_allow_all
        @api_view(['POST'])
        def submit_form(request):
            return Response({'success': True})

    Headers added:
        - Access-Control-Allow-Origin: *
        - Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
        - Access-Control-Allow-Headers: Content-Type, Authorization, ...
        - Access-Control-Max-Age: 86400
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        # Handle OPTIONS preflight
        if request.method == "OPTIONS":
            response = HttpResponse(status=200)
            return _add_cors_headers(response)

        # Call the view
        response = view_func(request, *args, **kwargs)

        # Add CORS headers
        return _add_cors_headers(response)

    # Disable CSRF for this view
    return csrf_exempt(wrapped_view)  # type: ignore


def cors_origins(
    allowed_origins: List[str],
    methods: str = DEFAULT_CORS_METHODS,
    headers: str = DEFAULT_CORS_HEADERS,
    max_age: int = DEFAULT_CORS_MAX_AGE,
    credentials: bool = True,
) -> Callable[[F], F]:
    """
    Decorator to allow CORS from specific origins only.

    Usage:
        @cors_origins([
            "https://myapp.com",
            "https://admin.myapp.com",
        ])
        def my_view(request):
            return JsonResponse({'success': True})

        # With credentials
        @cors_origins(
            ["https://myapp.com"],
            credentials=True,
        )
        def authenticated_view(request):
            return JsonResponse({'data': 'secret'})

    Args:
        allowed_origins: List of allowed origin URLs
        methods: Allowed HTTP methods
        headers: Allowed request headers
        max_age: Preflight cache duration in seconds
        credentials: Allow credentials (cookies, auth headers)
    """
    def decorator(view_func: F) -> F:
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            origin = request.META.get("HTTP_ORIGIN", "")

            # Check if origin is allowed
            if origin not in allowed_origins:
                # Handle OPTIONS without CORS headers (will fail preflight)
                if request.method == "OPTIONS":
                    return HttpResponse(status=200)
                # For other methods, just return response without CORS headers
                return view_func(request, *args, **kwargs)

            # Handle OPTIONS preflight
            if request.method == "OPTIONS":
                response = HttpResponse(status=200)
                return _add_cors_headers(
                    response,
                    origin=origin,
                    methods=methods,
                    headers=headers,
                    max_age=max_age,
                    credentials=credentials,
                )

            # Call the view
            response = view_func(request, *args, **kwargs)

            # Add CORS headers
            return _add_cors_headers(
                response,
                origin=origin,
                methods=methods,
                headers=headers,
                max_age=max_age,
                credentials=credentials,
            )

        return csrf_exempt(wrapped_view)  # type: ignore

    return decorator


def cors_exempt(view_func: F) -> F:
    """
    Alias for cors_allow_all.

    Named to match Django's csrf_exempt pattern.

    Usage:
        @cors_exempt
        def public_api(request):
            return JsonResponse({'public': True})
    """
    return cors_allow_all(view_func)


# For backwards compatibility and explicit naming
public_cors = cors_allow_all
open_cors = cors_allow_all
