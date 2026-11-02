"""Where the provider sends the browser back to, decided with ``django_cfg.core.site``.

The registered redirect URI of a site origin is ``<origin>/auth?provider=<id>``.
The origin is the browser's ``Origin`` header when it is one of the resolved
site's origins (``Site.accepts``); with no header it is the site's own
``site_url``. ``Site.accepts`` also takes subdomains of the registrable domain of a declared
origin (``accept_subdomains``); the provider still needs each such URI registered. An origin no site accepts is rejected, never replaced: a security
path does not guess. The callback ignores any client value and reuses the URI
stored with the state.
"""

from __future__ import annotations

from typing import List, Tuple
from urllib.parse import urlsplit

from django_cfg.core.exceptions import ConfigurationError
from django_cfg.core.site import normalize_origin, site_for, sites

from .base import OAuthError, OAuthErrorCode

CALLBACK_PATH = "/auth"


def redirect_uri_for(origin: str, provider_id: str) -> str:
    return f"{origin}{CALLBACK_PATH}?provider={provider_id}"


def registered_redirect_uris(provider_id: str) -> List[Tuple[str, str]]:
    """``(site key, URI)`` for every origin of every site: what to register at the provider."""
    return [
        (site.key, redirect_uri_for(origin, provider_id))
        for site in sites()
        for origin in sorted(site.origins)
    ]


def subdomain_accepted(provider_id: str) -> List[Tuple[str, str, str]]:
    """``(site key, accepted origins, URI pattern)`` per registrable domain a site accepts by the
    subdomain rule (``accept_subdomains``) beyond its declared origins. The provider still needs
    each URI registered exactly: acceptance here registers nothing there."""
    found = []
    for site in sites():
        for scheme, root, port in sorted(site.subdomain_roots(), key=str):
            suffix = f":{port}" if port else ""
            found.append((
                site.key,
                f"{scheme}://{root}{suffix} and {scheme}://*.{root}{suffix}",
                f"{scheme}://<origin>{suffix}{CALLBACK_PATH}?provider={provider_id}",
            ))
    return found


def resolve_redirect_uri(request, provider_id: str, requested: str = "") -> str:
    """The redirect URI for a new sign-in attempt. Raises ``OAuthError``."""
    try:
        site = site_for(request)
    except ConfigurationError as exc:
        raise OAuthError(OAuthErrorCode.MISSING_REDIRECT_URI) from exc

    if requested:
        parts = urlsplit(requested)
        origin = normalize_origin(requested)
        exact = (
            origin is not None
            and parts.path == CALLBACK_PATH
            and parts.query == f"provider={provider_id}"
            and not parts.fragment
            and not parts.username
            and site.accepts(origin)
        )
        if not exact:
            raise OAuthError(OAuthErrorCode.ORIGIN_NOT_ALLOWED)
        return redirect_uri_for(origin, provider_id)

    header = request.META.get("HTTP_ORIGIN")
    if header:
        if not site.accepts(header):
            raise OAuthError(OAuthErrorCode.ORIGIN_NOT_ALLOWED)
        return redirect_uri_for(normalize_origin(header), provider_id)
    if not site.site_url:
        raise OAuthError(OAuthErrorCode.MISSING_REDIRECT_URI)
    return redirect_uri_for(site.site_url, provider_id)
