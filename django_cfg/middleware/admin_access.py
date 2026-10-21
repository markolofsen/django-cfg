"""Answer 404 for the admin surface when it is closed to the caller.

Two cases, both silent (404, never 403: do not reveal that the route exists):

- `admin_access.enabled` is False: nothing under the admin prefix is served,
  even if a project still hard-codes `path("admin/", ...)`.
- `admin_access.allowed_networks` is set: only those networks get through.

Defence in depth. The primary control belongs at the proxy (Traefik,
Cloudflare). The caller IP is `REMOTE_ADDR`, which `RealIPMiddleware` rewrites
from CF-Connecting-IP / X-Forwarded-For; those headers are only trustworthy
when the app is reachable through the proxy alone.

The builder adds this middleware only when it can act, so a default project's
MIDDLEWARE is unchanged.
"""

from __future__ import annotations

import ipaddress
from typing import Callable, Optional

from django.http import Http404, HttpRequest, HttpResponse

from django_cfg.core.admin_access import get_admin_access, is_guarded_path


def client_ip(request: HttpRequest):
    """`REMOTE_ADDR` as an address object (IPv4-mapped IPv6 unwrapped), or None."""
    raw = request.META.get("REMOTE_ADDR", "")
    try:
        ip = ipaddress.ip_address(raw.strip())
    except ValueError:
        return None
    return ip.ipv4_mapped or ip if ip.version == 6 else ip


class AdminAccessMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        access = get_admin_access()
        if (not access.enabled or access.allowed_networks) and is_guarded_path(request.path):
            if not access.enabled or not self._allowed(request, access.networks):
                raise Http404
        return self.get_response(request)

    @staticmethod
    def _allowed(request: HttpRequest, networks) -> bool:
        ip = client_ip(request)
        return ip is not None and any(ip in network for network in networks)
