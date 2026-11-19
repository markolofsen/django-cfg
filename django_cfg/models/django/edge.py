"""Which proxies in front of Django are trusted, and how a request proves it came through Cloudflare.

`core/edge.py` resolves every request against this once; the client IP (`REMOTE_ADDR` after `RealIPMiddleware`),
`request.geo`, rate limits, Axes and login records all read that result. A header is never trusted for its own sake.

- `trust="cloudflare"` (default): walk the hops from the socket peer leftwards through `X-Forwarded-For`, skipping
  `trusted_proxies` (our own Traefik/nginx on private networks). The first other hop must be a Cloudflare address;
  only then are `CF-Connecting-IP`, `CF-IPCountry` and the other `CF-*` headers believed.
- `trust="secret"`: a Cloudflare Transform Rule adds `X-Edge-Auth: <secret>`; Django compares it in constant time and
  removes it. Topology-proof (another proxy in front, Cloudflare Tunnel).
- `trust="proxies"`: no Cloudflare; the client is the first hop that is not a trusted proxy.
- `trust="none"`: the socket peer is the client; no header is believed.

Env: `EDGE__TRUST`, `EDGE__TRUSTED_PROXIES` (comma-separated or JSON), `EDGE__SECRET`.
"""

from __future__ import annotations

import ipaddress
from typing import Annotated, Any, List, Literal, Optional

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

# Loopback, RFC 1918, carrier-grade NAT (Tailscale), link-local, IPv6 ULA: where our own proxies live.
DEFAULT_TRUSTED_PROXIES = [
    "127.0.0.0/8", "::1/128",
    "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16",
    "100.64.0.0/10",
    "169.254.0.0/16", "fe80::/10",
    "fc00::/7",
]

EdgeTrust = Literal["cloudflare", "secret", "proxies", "none"]


class EdgeConfig(BaseSettings):
    """Proxy trust for client IP and edge headers."""

    model_config = SettingsConfigDict(
        env_prefix="EDGE__",
        case_sensitive=False,
        validate_assignment=True,
        validate_default=True,
        extra="forbid",
    )

    trust: EdgeTrust = Field(
        default="cloudflare",
        description="How a request proves it came through the edge: cloudflare (hop check), secret, proxies, none",
    )

    trusted_proxies: Annotated[List[str], NoDecode] = Field(
        default_factory=lambda: list(DEFAULT_TRUSTED_PROXIES),
        description=(
            "CIDRs of our own proxies between the edge and Django. They are skipped when walking X-Forwarded-For. "
            "A client inside one of them is trusted to name another address, so keep it to networks you run."
        ),
    )

    secret: Optional[SecretStr] = Field(
        default=None,
        description="Value of X-Edge-Auth for trust='secret' (set by a Cloudflare Request Header Transform Rule)",
    )

    secret_header: str = Field(
        default="X-Edge-Auth",
        description="Header that carries the secret for trust='secret'",
    )

    @field_validator("trusted_proxies", mode="before")
    @classmethod
    def _split(cls, value: Any) -> Any:
        if isinstance(value, str):
            text = value.strip()
            if text.startswith("["):
                import json

                return json.loads(text)
            return [part.strip() for part in text.split(",") if part.strip()]
        return value

    @field_validator("trusted_proxies")
    @classmethod
    def _validate(cls, value: List[str]) -> List[str]:
        for item in value:
            try:
                ipaddress.ip_network(item, strict=False)
            except ValueError as exc:
                raise ValueError(f"edge.trusted_proxies: {item!r} is not a CIDR ({exc})") from exc
        return value

    @field_validator("secret_header")
    @classmethod
    def _header(cls, value: str) -> str:
        if not value or any(c in value for c in " :\r\n"):
            raise ValueError("edge.secret_header must be a plain header name")
        return value
