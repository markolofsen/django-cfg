"""Who is the client, and did this request come through our edge.

The one place that reads `X-Forwarded-For`, `CF-Connecting-IP` and the socket peer. Every other reader (rate limits,
Axes through `REMOTE_ADDR`, login records, analytics, `request.geo`) asks here. Trust rules: `models/django/edge.py`.

Measured on hel2 (2026-11-19): Django's socket peer is Traefik on a docker network and `X-Forwarded-For` ends with a
Cloudflare edge address. Code that took `X-Forwarded-For[0]` recorded the edge, not the visitor (every login row in
cmdop and mls for 90 days was a Cloudflare address).
"""

from __future__ import annotations

import hmac
import ipaddress
import logging
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Iterable, Optional, Tuple, Union

from .edge_ranges import CLOUDFLARE_IPV4, CLOUDFLARE_IPV6

if TYPE_CHECKING:
    from django.http import HttpRequest

    from ..models.django.edge import EdgeConfig

logger = logging.getLogger(__name__)

IPAddress = Union[ipaddress.IPv4Address, ipaddress.IPv6Address]
IPNetwork = Union[ipaddress.IPv4Network, ipaddress.IPv6Network]

#: META key where RealIPMiddleware keeps the address that really connected.
PEER_META = "DJANGO_CFG_PEER_ADDR"
_CACHE_ATTR = "_cfg_edge"
RANGES_FILE = "cloudflare-ips.txt"


@dataclass(frozen=True, slots=True)
class Edge:
    """The resolved request edge. `trusted` means edge headers (`CF-*`) may be believed."""

    trusted: bool
    client_ip: str
    peer: str
    via: str  # cloudflare | secret | proxy | direct


def parse_ip(value: str) -> Optional[IPAddress]:
    """An address from a header token: strips spaces, brackets and a port; unwraps IPv4-mapped IPv6."""
    text = (value or "").strip().strip('"')
    if not text:
        return None
    if text.startswith("["):
        text = text[1:].split("]", 1)[0]
    elif text.count(":") == 1:  # IPv4 with a port
        text = text.split(":", 1)[0]
    try:
        ip = ipaddress.ip_address(text)
    except ValueError:
        return None
    if ip.version == 6 and ip.ipv4_mapped:
        return ip.ipv4_mapped
    return ip


@lru_cache(maxsize=16)
def _networks(cidrs: Tuple[str, ...]) -> Tuple[IPNetwork, ...]:
    return tuple(ipaddress.ip_network(c, strict=False) for c in cidrs)


def _in(ip: IPAddress, networks: Iterable[IPNetwork]) -> bool:
    return any(ip.version == n.version and ip in n for n in networks)


def ranges_cache_path() -> Path:
    from .utils.runtime_paths import resolve_cache_dir

    return resolve_cache_dir("edge", RANGES_FILE)


@lru_cache(maxsize=1)
def cloudflare_networks() -> Tuple[IPNetwork, ...]:
    """Bundled Cloudflare ranges, or the refreshed copy in the cache dir when one exists and parses."""
    cidrs: Tuple[str, ...] = CLOUDFLARE_IPV4 + CLOUDFLARE_IPV6
    try:
        path = ranges_cache_path()
        if path.is_file():
            lines = tuple(line.strip() for line in path.read_text().splitlines() if line.strip() and not line.startswith("#"))
            if lines:
                return _networks(lines)
    except (OSError, ValueError) as exc:
        logger.warning("django-cfg edge: ignoring refreshed Cloudflare ranges (%s); using the bundled copy", exc)
    return _networks(cidrs)


def get_edge_config() -> "EdgeConfig":
    from ..models.django.edge import EdgeConfig
    from .state.registry import get_current_config

    config = get_current_config()
    edge = getattr(config, "edge", None) if config is not None else None
    return edge if edge is not None else _default_edge_config()


@lru_cache(maxsize=1)
def _default_edge_config() -> "EdgeConfig":
    from ..models.django.edge import EdgeConfig

    return EdgeConfig()


def _hops(meta) -> list:
    """Addresses from left (claimed client) to right (our socket peer). Unparseable tokens are dropped."""
    forwarded = [parse_ip(t) for t in (meta.get("HTTP_X_FORWARDED_FOR") or "").split(",")]
    peer = parse_ip(meta.get(PEER_META) or meta.get("REMOTE_ADDR") or "")
    return [ip for ip in forwarded if ip is not None] + ([peer] if peer is not None else [])


def resolve_edge(meta, config: Optional["EdgeConfig"] = None) -> Edge:
    """Resolve from a META mapping. Pure: no caching, no mutation (the secret header is removed by the middleware)."""
    config = config or get_edge_config()
    peer_raw = meta.get(PEER_META) or meta.get("REMOTE_ADDR") or ""
    peer_ip = parse_ip(peer_raw)
    peer = str(peer_ip) if peer_ip else ""

    if config.trust == "none":
        return Edge(False, peer, peer, "direct")

    proxies = _networks(tuple(config.trusted_proxies))
    hops = _hops(meta)
    # Walk right to left past our own proxies; `first` is the nearest address we do not run.
    first: Optional[IPAddress] = None
    first_at = -1
    for index in range(len(hops) - 1, -1, -1):
        if not _in(hops[index], proxies):
            first, first_at = hops[index], index
            break
    walked = str(first) if first is not None else (str(hops[0]) if hops else peer)

    if config.trust == "proxies":
        return Edge(False, walked, peer, "proxy" if walked != peer else "direct")

    connecting = parse_ip(meta.get("HTTP_CF_CONNECTING_IP") or "")
    if config.trust == "secret":
        secret = config.secret.get_secret_value() if config.secret else ""
        sent = meta.get("HTTP_" + config.secret_header.upper().replace("-", "_"), "")
        if secret and sent and hmac.compare_digest(sent.encode(), secret.encode()):
            return Edge(True, str(connecting) if connecting else walked, peer, "secret")
        return Edge(False, walked, peer, "proxy" if walked != peer else "direct")

    # trust == "cloudflare"
    if first is not None and _in(first, cloudflare_networks()):
        if connecting is None:  # no CF-Connecting-IP: the address Cloudflare appended, left of its edge
            connecting = hops[first_at - 1] if first_at > 0 else first
        return Edge(True, str(connecting), peer, "cloudflare")
    return Edge(False, walked, peer, "proxy" if walked != peer else "direct")


def get_edge(request: "HttpRequest") -> Edge:
    """The request's edge, resolved once and kept on the request."""
    cached = getattr(request, _CACHE_ATTR, None)
    if cached is None:
        cached = resolve_edge(request.META)
        try:
            setattr(request, _CACHE_ATTR, cached)
        except AttributeError:
            pass
    return cached


def get_client_ip(request) -> str:
    """The client address for a Django or DRF request (or anything with `.META`); "" when unknown."""
    inner = getattr(request, "_request", None)
    if inner is not None and hasattr(inner, "META"):
        request = inner
    if not hasattr(request, "META"):
        return ""
    return get_edge(request).client_ip


def strip_secret_header(meta, config: Optional["EdgeConfig"] = None) -> None:
    """Remove the edge secret so views, logs and error reports never see it."""
    config = config or get_edge_config()
    meta.pop("HTTP_" + config.secret_header.upper().replace("-", "_"), None)


__all__ = ["Edge", "PEER_META", "cloudflare_networks", "get_client_ip", "get_edge", "parse_ip", "resolve_edge"]
