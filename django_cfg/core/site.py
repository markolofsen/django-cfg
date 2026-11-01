"""One definition of "which site is this": ``Site``, and the resolver around it.

A project is one site by default, built from ``project_name``, ``site_url`` and
``api_url``. A Django that serves several sites declares ``DjangoConfig.sites``.
Either way, modules ask ``site_for(request)`` and never read those scalars for
anything a user sees.

The same registry is the one source of ALLOWED_HOSTS, CORS and CSRF origins
(``derive_access``): every site origin, every site's API host, the deployment
``api_url`` and the extra ``security_domains``. Nothing is typed twice.

Resolution order of ``site_for``: ``key=``, ``user=``, request ``Origin`` then
``Referer``, request ``Host``, the first declared site. ``Origin`` only selects
among registered sites, it never supplies a value. A flow that must not guess
(OAuth redirect, MCP consent) asks ``site.accepts(origin)`` and rejects on False.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple
from urllib.parse import urlparse, urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .exceptions import ConfigurationError

if TYPE_CHECKING:
    from .base.config_model import DjangoConfig

logger = logging.getLogger(__name__)

DEFAULT_KEY = "default"
DEFAULT_LOCALE = "en"

_KEY = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_LOCALE = re.compile(r"^[A-Za-z]{2,3}([_-][A-Za-z0-9]{2,8})*$")
_LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1", "0.0.0.0"}


# ---------------------------------------------------------------------------
# Value checks (shared with DjangoConfig's top-level fields)
# ---------------------------------------------------------------------------

def normalize_origin(value: str) -> Optional[str]:
    """``scheme://host[:port]`` in lower case, or None when ``value`` has no host."""
    try:
        parts = urlsplit(value.strip())
        host = parts.hostname
        if parts.scheme not in ("http", "https") or not host:
            return None
        default = {"http": 80, "https": 443}[parts.scheme]
        port = f":{parts.port}" if parts.port and parts.port != default else ""
    except ValueError:
        return None
    host = f"[{host}]" if ":" in host else host
    return f"{parts.scheme}://{host}{port}"


def check_origin(value: str) -> str:
    """An origin: scheme and host, no path, query or fragment."""
    origin = normalize_origin(value)
    parts = urlsplit(value.strip())
    if origin is None or parts.path not in ("", "/") or parts.query or parts.fragment:
        raise ValueError(f"{value!r} is not an origin like 'https://example.com'")
    return origin


def check_email(value: Optional[str]) -> Optional[str]:
    if value is not None and not _EMAIL.match(value):
        raise ValueError(f"{value!r} is not an email address")
    return value


def check_logo_url(value: Optional[str]) -> Optional[str]:
    if value is not None and normalize_origin(value) is None:
        raise ValueError(f"{value!r} is not an absolute http(s) URL")
    return value


def check_locale(value: Optional[str]) -> Optional[str]:
    if value is not None and not _LOCALE.match(value):
        raise ValueError(f"{value!r} is not a locale tag like 'en' or 'pt-BR'")
    return value


def _netloc(origin: str) -> str:
    return urlsplit(origin).netloc.lower()


# ---------------------------------------------------------------------------
# Declaration and resolved value
# ---------------------------------------------------------------------------

class SiteConfig(BaseModel):
    """One site a Django serves. Required: ``key``, ``name``, ``site_url``.

    Unset ``api_url`` is the deployment ``api_url`` (set it only for a site with its
    own API host), unset ``from_email`` inherits ``email.default_from``, unset
    ``locale`` is ``en`` (``DjangoConfig.default_locale`` is for single-site). ``support_email``
    and ``logo_url`` have no inheritance.
    """

    model_config = ConfigDict(frozen=True, extra="forbid", str_strip_whitespace=True)

    key: str = Field(..., description="Stable id: 'caribbean', 'bali'. Lower case; jobs carry it.")
    name: str = Field(..., min_length=1, max_length=100, description="What users read: mail subjects, footers and sender name.")
    site_url: str = Field(..., description="Public web origin: 'https://example.com'.")
    api_url: Optional[str] = Field(
        default=None, description="Backend origin of this site. Default: the deployment api_url.",
    )
    extra_origins: Tuple[str, ...] = Field(
        default=(), description="Other web origins of the same site (portal, studio).",
    )
    support_email: Optional[str] = Field(default=None, description="Shown in mail footers.")
    from_email: Optional[str] = Field(default=None, description="Sender address. Default: email.default_from.")
    from_name: Optional[str] = Field(default=None, description="Sender display name. Default: name.")
    logo_url: Optional[str] = Field(default=None, description="Absolute URL of the logo for mail.")
    locale: Optional[str] = Field(default=None, description="Default locale for mail and copy. Default: default_locale.")

    @field_validator("key")
    @classmethod
    def _key(cls, v: str) -> str:
        if not _KEY.match(v):
            raise ValueError("key is lower case letters, digits, '_' or '-' (e.g. 'bali')")
        return v

    @field_validator("site_url")
    @classmethod
    def _origin(cls, v: str) -> str:
        return check_origin(v)

    @field_validator("api_url")
    @classmethod
    def _api_origin(cls, v: Optional[str]) -> Optional[str]:
        return check_origin(v) if v is not None else None

    @field_validator("extra_origins")
    @classmethod
    def _origins(cls, v: Tuple[str, ...]) -> Tuple[str, ...]:
        return tuple(dict.fromkeys(check_origin(o) for o in v))

    @field_validator("support_email", "from_email")
    @classmethod
    def _email(cls, v: Optional[str]) -> Optional[str]:
        return check_email(v)

    @field_validator("logo_url")
    @classmethod
    def _logo(cls, v: Optional[str]) -> Optional[str]:
        return check_logo_url(v)

    @field_validator("locale")
    @classmethod
    def _locale(cls, v: Optional[str]) -> Optional[str]:
        return check_locale(v)

    @model_validator(mode="after")
    def _hosts_differ(self) -> "SiteConfig":
        if self.api_url is not None and _netloc(self.api_url) == _netloc(self.site_url):
            raise ValueError(
                f"site {self.key!r}: api_url and site_url share the host {_netloc(self.site_url)!r}"
            )
        return self


@dataclass(frozen=True)
class Site:
    """A resolved site. Read it through ``site_for``; never build one by hand."""

    key: str
    name: str
    site_url: str
    api_url: str
    origins: frozenset[str]
    support_email: Optional[str]
    from_email: Optional[str]
    from_name: str
    logo_url: Optional[str]
    locale: str
    # Fields taken from the deployment, not declared on the site: api_url, from_email.
    # show_config marks them.
    inherited: frozenset[str] = field(default=frozenset(), compare=False)

    def url(self, path: str = "") -> str:
        """``site_url`` + path: the only place a link to the site is built."""
        if path and not path.startswith("/"):
            path = "/" + path
        return self.site_url + path

    def accepts(self, origin: Optional[str]) -> bool:
        """True when ``origin`` is one of this site's web origins. Security paths reject on False."""
        normalized = normalize_origin(origin) if origin else None
        return normalized in self.origins

    def as_context(self) -> dict[str, Any]:
        """Template vocabulary: ``project_name`` and ``site_name`` are both ``name``."""
        return {
            "project_name": self.name,
            "site_name": self.name,
            "site_url": self.site_url,
            "support_email": self.support_email,
            "logo_url": self.logo_url,
            "site": self,
        }


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

def _web_origins_from_domains(config: "DjangoConfig") -> set[str]:
    """Web origins named in ``security_domains``: no ``api.``/``mcp.`` hosts, no
    local or single-label hosts outside development."""
    api_host = (urlsplit(config.api_url).hostname or "").lower()
    found: set[str] = set()
    for entry in config.security_domains:
        entry = entry.strip().lower()
        if not entry or "*" in entry or entry.startswith("."):
            continue
        explicit = "://" in entry
        parts = urlsplit(entry if explicit else f"//{entry}")
        host = parts.hostname
        if not host or host == api_host or host.startswith(("api.", "mcp.")):
            continue
        local = host in _LOCAL_HOSTS or "." not in host
        if local and not config.is_development:
            continue
        scheme = parts.scheme if explicit else ("http" if local else "https")
        port = f":{parts.port}" if parts.port else ""
        found.add(f"{scheme}://{host}{port}")
    return found


def _synthesize(config: "DjangoConfig") -> Site:
    email = config.email
    site_url = config.site_url.rstrip("/")
    api_url = config.api_url.rstrip("/")
    origins = _web_origins_from_domains(config)
    own = normalize_origin(site_url)
    if own:
        origins.add(own)
    return Site(
        key=DEFAULT_KEY,
        name=config.project_name,
        site_url=site_url,
        api_url=api_url,
        origins=frozenset(origins),
        support_email=config.support_email,
        from_email=email.default_from if email else None,
        from_name=(email.default_from_name if email else None) or config.project_name,
        logo_url=config.logo_url,
        locale=config.default_locale or DEFAULT_LOCALE,
    )


def _resolve(config: "DjangoConfig", declared: SiteConfig) -> Site:
    email = config.email
    inherited: set[str] = set()
    api_url = declared.api_url
    if api_url is None:
        api_url = config.api_url.rstrip("/")
        inherited.add("api_url")
    from_email = declared.from_email
    if from_email is None and email and email.default_from:
        from_email = email.default_from
        inherited.add("from_email")
    return Site(
        key=declared.key,
        name=declared.name,
        site_url=declared.site_url,
        api_url=api_url,
        origins=frozenset({declared.site_url, *declared.extra_origins}),
        support_email=declared.support_email,
        from_email=from_email,
        from_name=declared.from_name or declared.name,
        logo_url=declared.logo_url,
        locale=declared.locale or DEFAULT_LOCALE,
        inherited=frozenset(inherited),
    )


def resolve_sites(config: "DjangoConfig") -> Tuple[Site, ...]:
    """The sites of ``config``: its ``sites``, or one synthesised ``default`` site. Cached on the config."""
    cached = config._sites
    if cached is None:
        cached = (
            tuple(_resolve(config, s) for s in config.sites)
            if config.sites
            else (_synthesize(config),)
        )
        config._sites = cached
    return cached


# ---------------------------------------------------------------------------
# Derived access: ALLOWED_HOSTS, CORS and CSRF origins
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SiteAccess:
    """Hosts and origins a deployment answers to, derived from its registry."""

    domains: Tuple[str, ...]  # unique entries: ``host`` or ``scheme://host[:port]``
    allowed_hosts: Tuple[str, ...]
    cors_origins: Tuple[str, ...]
    csrf_origins: Tuple[str, ...]


def declared_urls(config: "DjangoConfig") -> list[str]:
    """Every URL the registry declares: the deployment ``api_url`` and, per site, its
    API URL, web origin and extra origins. Single-site: ``api_url`` and ``site_url``."""
    urls = [config.api_url]
    for site in resolve_sites(config):
        urls += [site.api_url, site.site_url]
        if config.sites:
            urls += sorted(site.origins - {site.site_url})
    return urls


def _split_domain(domain: str) -> Tuple[Optional[str], str, Optional[int]]:
    """``(scheme or None, lower-case host, port)`` of a ``security_domains`` style entry."""
    explicit = domain.startswith(("http://", "https://"))
    parsed = urlparse(domain if explicit else f"http://{domain}")
    host = (parsed.hostname or parsed.netloc.split(":")[0]).lower()
    return (parsed.scheme if explicit else None), host, parsed.port


def _hostport(domain: str) -> str:
    _, host, port = _split_domain(domain)
    return f"{host}:{port}" if port else host


def _origin_of(url: str) -> Optional[str]:
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return None
        port = f":{parsed.port}" if parsed.port else ""
        return f"{parsed.scheme}://{parsed.hostname}{port}"
    except ValueError:
        return None


def _unique_domains(domains: list[str]) -> list[str]:
    """Drop repeats by host and port, ignoring scheme. The first spelling wins."""
    seen: Dict[str, str] = {}
    unique: list[str] = []
    for domain in domains:
        if not domain or not domain.strip():
            continue
        domain = domain.strip()
        try:
            scheme, host, port = _split_domain(domain)
            key = f"{host}:{port}" if port else host
            if key in seen:
                continue
            normalized = (f"{scheme}://{host}" + (f":{port}" if port else "")) if scheme else domain.lower()
        except ValueError:
            key = normalized = domain.lower()
            if normalized in seen.values():
                continue
        seen[key] = normalized
        unique.append(normalized)
    return unique


def derive_access(config: "DjangoConfig") -> SiteAccess:
    """ALLOWED_HOSTS, CORS and CSRF origins: ``security_domains`` (the extras) plus
    everything the registry declares. Bare entries take ``https`` in production, ``http`` otherwise."""
    extra = [o for o in (_origin_of(u) for u in declared_urls(config)) if o]
    domains = _unique_domains([*config.security_domains, *extra])
    scheme = "https" if config.is_production else "http"

    hosts: list[str] = []
    origins: list[str] = []
    for domain in domains:
        full = domain if domain.startswith(("http://", "https://")) else f"{scheme}://{domain}"
        try:
            parsed = urlparse(full)
            host = parsed.hostname or parsed.netloc.split(":")[0]
            port = f":{parsed.port}" if parsed.port else ""
            origin = f"{parsed.scheme}://{parsed.hostname}{port}"
        except ValueError as exc:
            import warnings

            warnings.warn(f"Failed to parse domain '{domain}': {exc}", UserWarning, stacklevel=2)
            continue
        if host:
            hosts.append(host)
        if parsed.hostname:
            origins.append(origin)
    return SiteAccess(
        domains=tuple(domains),
        allowed_hosts=tuple(dict.fromkeys(hosts)),
        cors_origins=tuple(dict.fromkeys(origins)),
        csrf_origins=tuple(dict.fromkeys(origins)),
    )


def redundant_security_domains(config: "DjangoConfig") -> list[Tuple[str, str]]:
    """``(entry, owner)`` for each ``security_domains`` entry that repeats a host the
    registry already declares. Only with ``sites``: a single-site project lists its
    hosts there on purpose."""
    if not config.sites:
        return []
    owners: Dict[str, str] = {}
    for site in resolve_sites(config):
        urls = [*site.origins] + ([] if "api_url" in site.inherited else [site.api_url])
        for url in urls:
            owners.setdefault(_hostport(url), f"site {site.key!r}")
    owners.setdefault(_hostport(config.api_url), "the deployment api_url")
    found = []
    for entry in config.security_domains:
        try:
            owner = owners.get(_hostport(entry.strip())) if entry.strip() else None
        except ValueError:
            continue
        if owner:
            found.append((entry, owner))
    return found


def describe_sites(config: "DjangoConfig") -> list[str]:
    """The resolved sites of ``config``, one block of lines per site, for CLI output.

    Values a site takes from the deployment are marked ``(inherited)``."""
    lines: list[str] = []
    for site in resolve_sites(config):
        def mark(name: str, site: Site = site) -> str:
            return " (inherited)" if name in site.inherited else ""

        lines.append(f"{site.key}: {site.name}  {site.site_url}  api {site.api_url}{mark('api_url')}")
        lines.append(f"    origins  {', '.join(sorted(site.origins))}")
        lines.append(
            f"    mail     from {site.from_name} <{site.from_email or 'DEFAULT_FROM_EMAIL'}>{mark('from_email')}"
            f"  reply-to {site.support_email or '-'}  locale {site.locale}"
        )
    return lines


def sites() -> Tuple[Site, ...]:
    """Every site of the running config; empty when django-cfg is not configured."""
    from .state.registry import get_current_config

    config = get_current_config()
    return resolve_sites(config) if config is not None else ()


def site_for(request: Any = None, *, key: Optional[str] = None, user: Any = None) -> Site:
    """The site a request, job or user belongs to. Always returns a registered site.

    Order: ``key`` (background jobs), ``user`` (first registration source),
    request ``Origin`` then ``Referer``, request ``Host``, first declared site.
    An unknown ``key`` is logged and falls through.
    """
    registry = sites()
    if not registry:
        raise ConfigurationError("django_cfg is not configured: no current DjangoConfig, so no sites")
    if key is not None:
        for site in registry:
            if site.key == key:
                return site
        logger.warning("site_for: unknown site key %r, falling back", key)
    if user is not None:
        found = _site_of_user(user, registry)
        if found:
            return found
    if request is not None:
        found = getattr(request, "_django_cfg_site", None)
        if found is None:
            found = _site_of_request(request, registry)
            if found:
                try:
                    request._django_cfg_site = found
                except AttributeError:
                    pass
        if found:
            return found
    return registry[0]


def resolve_source_url(raw: Optional[str]) -> Optional[str]:
    """A client-supplied page URL as the ``site_url`` of the site it belongs to.

    ``source_url`` is the only per-user trace of the site, and it is client
    controlled: it is accepted only as a way to *select* a registered site (its
    origin is in some site's ``origins``). Anything else, a foreign host or a
    bare string, becomes the default site's ``site_url``. Blank stays None.
    Without a configured project the value is returned as given.
    """
    raw = (raw or "").strip()
    if not raw:
        return None
    registry = sites()
    if not registry:
        return raw
    return (_by_origin(raw, registry) or registry[0]).site_url


def site_key(request: Any) -> str:
    """The key of ``request``'s site. Jobs take the key, not the request."""
    return site_for(request).key


def _by_origin(origin: Optional[str], registry: Tuple[Site, ...]) -> Optional[Site]:
    normalized = normalize_origin(origin) if origin else None
    if normalized is None:
        return None
    return next((s for s in registry if normalized in s.origins), None)


def _site_of_user(user: Any, registry: Tuple[Site, ...]) -> Optional[Site]:
    try:
        link = user.user_registration_sources.select_related("source").order_by("registration_date").first()
        return _by_origin(link.source.url, registry) if link else None
    except Exception:  # noqa: BLE001 - no table, anonymous or unsaved user: not a signal
        return None


def _site_of_request(request: Any, registry: Tuple[Site, ...]) -> Optional[Site]:
    meta = request.META
    found = _by_origin(meta.get("HTTP_ORIGIN"), registry) or _by_origin(meta.get("HTTP_REFERER"), registry)
    if found:
        return found

    host = (meta.get("HTTP_HOST") or "").strip().lower()
    if host:
        bare = host.rsplit(":", 1)[0] if not host.endswith("]") else host
        for exact in (True, False):
            for site in registry:
                for url in (site.api_url, site.site_url):
                    if (_netloc(url) == host) if exact else (urlsplit(url).hostname == bare):
                        return site
        _warn_if_host_was_rewritten(meta, registry)
    return None


_warned_forwarded_host = False


def _warn_if_host_was_rewritten(meta: dict, registry: Tuple[Site, ...]) -> None:
    """Warn once: the proxy forwarded a site host but Django's ``Host`` is another one."""
    global _warned_forwarded_host
    if _warned_forwarded_host:
        return
    from django.conf import settings

    forwarded = (meta.get("HTTP_X_FORWARDED_HOST") or "").split(",")[0].strip().lower()
    if not forwarded or getattr(settings, "USE_X_FORWARDED_HOST", False):
        return
    if any(forwarded in (_netloc(s.api_url), _netloc(s.site_url)) for s in registry):
        _warned_forwarded_host = True
        logger.warning(
            "Request Host %r is not a site host but X-Forwarded-Host %r is. The proxy rewrites Host; "
            "keep the public Host in the proxy, or set USE_X_FORWARDED_HOST = True behind a trusted proxy.",
            meta.get("HTTP_HOST"), forwarded,
        )
