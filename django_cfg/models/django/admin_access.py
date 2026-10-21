"""Where the Django admin lives and who may reach it.

Scanners probe `/admin/` on every host. This model makes the admin's
availability and location core-config settings instead of a line hard-wired in
each project's `urls.py`:

- `enabled`: False mounts nothing (the route 404s) and nothing links to it.
- `path`: the URL prefix. Pick an unguessable one in production.
- `allowed_networks`: optional CIDR allowlist; everyone else gets a plain 404.

The allowlist is defence in depth. The primary control belongs at the proxy
(Traefik, Cloudflare), which can refuse a request before Django sees it.

Env (process environment, the same `__` nested style as `DATABASE__URL`):
`ADMIN_ACCESS__ENABLED`, `ADMIN_ACCESS__PATH`, `ADMIN_ACCESS__ALLOWED_NETWORKS`
(comma-separated, or a JSON list). A value passed in code wins over env.
"""

from __future__ import annotations

import ipaddress
import re
from functools import lru_cache
from typing import Annotated, Any, List, Tuple, Union

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

DEFAULT_ADMIN_PATH = "admin/"

# One or more URL-safe segments (RFC 3986 unreserved), each followed by "/".
# Excludes "", leading "/", "//", "%", "?", "#", spaces; ".." is rejected below.
_PATH_RE = re.compile(r"^[A-Za-z0-9._~-]+(/[A-Za-z0-9._~-]+)*/$")

IPNetwork = Union[ipaddress.IPv4Network, ipaddress.IPv6Network]


@lru_cache(maxsize=32)
def parse_networks(networks: Tuple[str, ...]) -> Tuple[IPNetwork, ...]:
    """Parse CIDR strings once; a bare address becomes a /32 or /128."""
    return tuple(ipaddress.ip_network(n, strict=False) for n in networks)


class AdminAccessConfig(BaseSettings):
    """Availability, location and network allowlist of the Django admin."""

    model_config = SettingsConfigDict(
        env_prefix="ADMIN_ACCESS__",
        case_sensitive=False,
        validate_assignment=True,
        validate_default=True,
        extra="forbid",
    )

    enabled: bool = Field(
        default=True,
        description=(
            "False: the admin route is not mounted (404), nothing links to it, "
            "and shell/management commands are unaffected."
        ),
    )

    path: str = Field(
        default=DEFAULT_ADMIN_PATH,
        description=(
            "URL prefix of the admin: no leading slash, ends with a slash, "
            "URL-safe characters only. Use an unguessable value in production: "
            "python -c 'import secrets; print(secrets.token_urlsafe(16) + \"/\")'"
        ),
    )

    allowed_networks: Annotated[List[str], NoDecode] = Field(
        default_factory=list,
        description=(
            "CIDR allowlist (IPv4/IPv6). Non-empty: any request under the admin "
            "prefix from outside it gets 404, never 403. Matched against "
            "REMOTE_ADDR, which RealIPMiddleware sets from the proxy headers. "
            "Empty: no restriction."
        ),
    )

    @field_validator("path")
    @classmethod
    def _validate_path(cls, value: str) -> str:
        if ".." in value or not _PATH_RE.match(value):
            raise ValueError(
                f"admin_access.path {value!r} is invalid: use URL-safe characters "
                "(letters, digits, '-', '_', '.', '~', inner '/'), no leading slash, "
                "no '..', and end with a slash, e.g. 'k3J9x-Qw2/'"
            )
        return value

    @field_validator("allowed_networks", mode="before")
    @classmethod
    def _split_networks(cls, value: Any) -> Any:
        """Env gives a string: accept a JSON list or comma-separated CIDRs."""
        if isinstance(value, str):
            text = value.strip()
            if text.startswith("["):
                import json

                return json.loads(text)
            return [part.strip() for part in text.split(",") if part.strip()]
        return value

    @field_validator("allowed_networks")
    @classmethod
    def _validate_networks(cls, value: List[str]) -> List[str]:
        for item in value:
            try:
                ipaddress.ip_network(item, strict=False)
            except ValueError as exc:
                raise ValueError(f"admin_access.allowed_networks: {item!r} is not a CIDR ({exc})") from exc
        return value

    @property
    def is_default_path(self) -> bool:
        return self.path == DEFAULT_ADMIN_PATH

    @property
    def networks(self) -> Tuple[IPNetwork, ...]:
        return parse_networks(tuple(self.allowed_networks))
