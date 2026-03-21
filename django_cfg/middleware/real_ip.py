"""Real IP middleware — fixes REMOTE_ADDR behind proxies.

Overwrites REMOTE_ADDR with the real client IP from proxy headers
(Cloudflare, nginx, traefik). All downstream code (Django, DRF, Axes,
ratelimit) automatically sees the correct IP.

Must be placed early in MIDDLEWARE — before any security/auth middleware.
"""


class RealIPMiddleware:
    """Overwrite REMOTE_ADDR with real client IP from proxy headers."""

    # Header precedence (most trusted first)
    HEADERS = [
        'HTTP_CF_CONNECTING_IP',     # Cloudflare
        'HTTP_X_FORWARDED_FOR',      # nginx, traefik, AWS ALB
        'HTTP_X_REAL_IP',            # nginx alternative
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        for header in self.HEADERS:
            value = request.META.get(header)
            if value:
                # X-Forwarded-For: client, proxy1, proxy2 — take first
                real_ip = value.split(',')[0].strip()
                if real_ip:
                    request.META['REMOTE_ADDR'] = real_ip
                    break

        return self.get_response(request)
