"""
Django-CFG Middleware: Prevent Search Engine Indexing

Universal middleware that adds X-Robots-Tag header to prevent search engines
from indexing the entire Django project.

This ensures that your Django application (admin panels, APIs, internal tools, etc.)
is not exposed in search engine results.
"""

from django.http import HttpRequest, HttpResponse
from typing import Callable


class NoIndexMiddleware:
    """
    Universal middleware to prevent search engine indexing of entire Django project.

    Adds X-Robots-Tag: noindex, nofollow header to ALL responses.
    Adds Cache-Control headers to sensitive paths (/cfg/, /admin/).

    Usage:
        Add to MIDDLEWARE in settings.py:
        ```python
        MIDDLEWARE = [
            ...
            'django_cfg.core.middleware.noindex.NoIndexMiddleware',
            ...
        ]
        ```

    Headers Added:
        - X-Robots-Tag: noindex, nofollow (ALL responses)
        - Cache-Control: no-cache, no-store, must-revalidate (for /cfg/* and /admin/* paths)

    Example Response:
        HTTP/1.1 200 OK
        X-Robots-Tag: noindex, nofollow
        Cache-Control: no-cache, no-store, must-revalidate
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        """
        Initialize middleware.

        Args:
            get_response: Next middleware or view in chain
        """
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Process request and add noindex header to ALL responses.

        Args:
            request: HTTP request

        Returns:
            HTTP response with X-Robots-Tag header on all responses
        """
        # Get response from next middleware/view
        response = self.get_response(request)

        # Add X-Robots-Tag header to ALL responses to prevent indexing
        response['X-Robots-Tag'] = 'noindex, nofollow'

        # Add Cache-Control to prevent caching for sensitive paths (security best practice)
        if request.path.startswith('/cfg/') or request.path.startswith('/admin/'):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'

        return response
