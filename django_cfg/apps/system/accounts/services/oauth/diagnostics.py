"""What can go wrong with a sign-in setup, found before a user hits it.

One list of findings feeds both Django's system checks (``manage.py check``,
``runserver``, ``migrate``) and ``manage.py oauth_check``.

    django_cfg.W030  a provider has only one of client id / client secret
    django_cfg.W031  site_url is not https in production
    django_cfg.W032  site_url host is missing from security_domains
    django_cfg.W033  Google client id is not shaped like a Google client id
    django_cfg.W034  production without a Redis cache: sign-in rate limits are per process
    django_cfg.W035  production without RealIPMiddleware: rate limits see the proxy's IP
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List
from urllib.parse import urlsplit

from django.conf import settings

from django_cfg.models.api.oauth import GitHubOAuthConfig, GoogleOAuthConfig

from .registry import all_providers

GOOGLE_CLIENT_ID_SUFFIX = ".apps.googleusercontent.com"
CONFIG_CLASSES = {"github": GitHubOAuthConfig, "google": GoogleOAuthConfig}


@dataclass(frozen=True)
class Finding:
    id: str
    message: str
    hint: str = ""
    provider: str = ""


def _half_configured(provider) -> bool:
    """One of id/secret set: in the config object or, with no object, in the environment."""
    config = provider.config()
    if config is not None:
        return bool(config.client_id) != bool(config.client_secret)
    id_name, secret_name = CONFIG_CLASSES[provider.id].env_names()
    return bool(os.environ.get(id_name, "").strip()) != bool(os.environ.get(secret_name, "").strip())


def _security_domain_hosts(config) -> List[str]:
    hosts = []
    for entry in config.security_domains:
        entry = entry.strip().lower()
        parts = urlsplit(entry if "://" in entry else f"//{entry}")
        if parts.hostname or entry.startswith("."):
            hosts.append(parts.hostname or entry)
    return hosts


def _host_listed(host: str, listed: List[str]) -> bool:
    return any(host == h or (h.startswith(".") and (host == h[1:] or host.endswith(h))) for h in listed)


def _host_declared(config, host: str) -> bool:
    """True when the registry already allows ``host``: it is a declared URL's host, or a
    subdomain of a declared URL's registrable domain (``accept_subdomains``)."""
    from django_cfg.core.site import _declared_roots, declared_urls, registrable_domain

    if any(urlsplit(u if "://" in u else f"//{u}").hostname == host for u in declared_urls(config)):
        return True
    return getattr(config, "accept_subdomains", True) and registrable_domain(host) in _declared_roots(config)


def collect_findings() -> List[Finding]:
    from django_cfg.core.site import sites
    from django_cfg.core.state.registry import get_current_config

    findings: List[Finding] = []
    providers = all_providers()

    for provider in providers:
        if _half_configured(provider):
            id_name, secret_name = CONFIG_CLASSES[provider.id].env_names()
            findings.append(Finding(
                "django_cfg.W030",
                f"{provider.name} sign-in is half configured: client id or client secret is missing, so it stays off.",
                f"Set both {id_name} and {secret_name} (or neither).",
                provider.id,
            ))

    enabled = [p for p in providers if p.is_enabled()]
    google = next((p for p in enabled if p.id == "google"), None)
    if google is not None and not google.config().client_id.endswith(GOOGLE_CLIENT_ID_SUFFIX):
        findings.append(Finding(
            "django_cfg.W033",
            f"The Google client id does not end with {GOOGLE_CLIENT_ID_SUFFIX}.",
            "Copy the client id of a 'Web application' client from Google Cloud > Google Auth platform > Clients.",
            "google",
        ))

    config = get_current_config()
    if not enabled or config is None:
        return findings

    registry = sites()
    if config.is_production:
        for site in registry:
            if not site.site_url.startswith("https://"):
                findings.append(Finding(
                    "django_cfg.W031",
                    f"Site {site.key!r}: site_url {site.site_url} is not https, but sign-in providers only "
                    "accept https redirect URIs in production.",
                    "Set site_url to the public https origin.",
                ))
        cache_backend = settings.CACHES.get("default", {}).get("BACKEND", "")
        if "redis" not in cache_backend.lower():
            findings.append(Finding(
                "django_cfg.W034",
                f"Production uses the cache backend {cache_backend or 'none'}: sign-in rate limits are not shared between workers.",
                "Set redis_url so the default cache is Redis.",
            ))
        if not any(m.endswith("RealIPMiddleware") for m in settings.MIDDLEWARE):
            findings.append(Finding(
                "django_cfg.W035",
                "RealIPMiddleware is not installed: behind a proxy every client shares one IP and the sign-in "
                "rate limit trips for everyone.",
                "Keep the django-cfg middleware stack, or rewrite REMOTE_ADDR from the proxy's header.",
            ))

    # Declared sites are allowed automatically; only the synthesised site can be left out by hand.
    listed = _security_domain_hosts(config)
    for site in () if config.sites else registry:
        host = urlsplit(site.site_url).hostname or ""
        if host and not _host_listed(host, listed) and not _host_declared(config, host):
            findings.append(Finding(
                "django_cfg.W032",
                f"Site {site.key!r}: the host {host} is not in security_domains, so browsers on it may be refused (CORS/CSRF).",
                "Add the host to security_domains.",
            ))
    return findings
