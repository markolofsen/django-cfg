"""
Middleware that catches DisallowedHost and logs an actionable hint.

Django's default error: "Invalid HTTP_HOST header: 'myhost'. You may need to add 'myhost' to ALLOWED_HOSTS."
This middleware replaces it with a django-cfg specific hint.
"""

import logging

from django.core.exceptions import DisallowedHost
from django.http import HttpResponseBadRequest

logger = logging.getLogger("django.security")


class AllowedHostsHintMiddleware:
    """Log a django-cfg hint when a host is rejected by ALLOWED_HOSTS."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            # Access request.get_host() to trigger DisallowedHost early
            request.get_host()
        except DisallowedHost:
            host = request.META.get("HTTP_HOST", "unknown")
            logger.error(
                "Host '%s' not in ALLOWED_HOSTS. "
                "Fix: add '%s' to security_domains in your DjangoConfig, "
                "or set DJANGO_INTERNAL_HOSTS=%s in Docker env.",
                host, host.split(":")[0], host.split(":")[0],
            )
            return HttpResponseBadRequest(f"Invalid host: {host}")

        return self.get_response(request)
