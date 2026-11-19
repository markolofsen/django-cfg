"""Real IP middleware: `REMOTE_ADDR` becomes the client, resolved by `core/edge.py`.

Proxy headers are believed only as far as `edge` config allows (Cloudflare hop check by default), so a client that
reaches the origin directly cannot name its own address. Code that reads `REMOTE_ADDR` (Django, Axes, DRF throttles
with NUM_PROXIES=0, the admin allow-list) sees the resolved client. The socket peer stays in
`META["DJANGO_CFG_PEER_ADDR"]`; `request.edge` carries the whole result.

Must be first in MIDDLEWARE.
"""

from django_cfg.core.edge import PEER_META, get_edge, strip_secret_header


class RealIPMiddleware:
    """Overwrite REMOTE_ADDR with the client IP the edge rules accept."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.META.setdefault(PEER_META, request.META.get("REMOTE_ADDR", ""))
        edge = get_edge(request)
        strip_secret_header(request.META)
        request.edge = edge
        if edge.client_ip:
            request.META["REMOTE_ADDR"] = edge.client_ip
        return self.get_response(request)
