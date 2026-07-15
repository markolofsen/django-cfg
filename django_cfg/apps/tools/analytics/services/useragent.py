"""User-Agent parsing and bot detection.

The raw UA string is NEVER stored — it is reduced to (browser, os, device) here
and discarded. Unique-UA cardinality is exactly what blew up GoatCounter's
database; keeping the string would hand us the same problem.

Two traps, both load-bearing:

1. uap-core only tags *self-declaring* spiders. ``python-requests`` and ``curl``
   come back as device=None, i.e. NOT a bot. A UA parser alone is not a bot
   filter, which is why ``looks_like_bot`` exists.

2. The parse cache must be BOUNDED. This runs on a public, unauthenticated
   ingest endpoint, so an unbounded cache keyed on an attacker-controlled string
   is a memory-exhaustion vector.

``ua-parser`` (Apache-2.0) is an optional dependency: absent it, we degrade to
"unknown" rather than failing the ingest. Analytics must never break the app.
"""

from __future__ import annotations

import re
from functools import lru_cache

from ..models.session import DeviceType

try:
    from ua_parser import user_agent_parser as _uap
except ImportError:  # pragma: no cover - optional dependency
    _uap = None


# Non-self-declaring clients that uap-core does not flag. Deliberately short:
# the JS beacon is the real first-line filter (honest crawlers do not run JS).
_BOT_RE = re.compile(
    r"bot|crawl|spider|slurp|curl|wget|python-requests|httpx|axios|"
    r"headless|phantom|puppeteer|playwright|selenium|lighthouse|"
    r"monitor|uptime|pingdom|scrapy|go-http-client|java/|okhttp",
    re.IGNORECASE,
)

_MOBILE_RE = re.compile(r"mobile|iphone|ipod|android.*mobile", re.IGNORECASE)
_TABLET_RE = re.compile(r"tablet|ipad|playbook|silk", re.IGNORECASE)


def looks_like_bot(user_agent: str) -> bool:
    """Cheap pre-filter. Runs before any parsing."""
    if not user_agent:
        # Every real browser sends a UA. An empty one is a script.
        return True
    return bool(_BOT_RE.search(user_agent))


@lru_cache(maxsize=4096)  # BOUNDED. See module docstring.
def parse(user_agent: str) -> tuple[str, str, str]:
    """Return ``(browser, os, device)``. Never raises."""
    if looks_like_bot(user_agent):
        return ("", "", DeviceType.BOT)

    if _uap is None:
        return ("", "", _device_from_regex(user_agent))

    try:
        parsed = _uap.Parse(user_agent)
        browser = (parsed.get("user_agent") or {}).get("family") or ""
        os_name = (parsed.get("os") or {}).get("family") or ""
        device_info = parsed.get("device") or {}
    except Exception:
        # A malformed UA must never 500 the ingest endpoint.
        return ("", "", DeviceType.UNKNOWN)

    if browser == "Other":
        browser = ""
    if os_name == "Other":
        os_name = ""

    return (browser[:32], os_name[:32], _device_from_parsed(device_info, user_agent))


def _device_from_parsed(device_info: dict, user_agent: str) -> str:
    family = (device_info.get("family") or "").lower()
    if family == "spider":
        return DeviceType.BOT
    return _device_from_regex(user_agent)


def _device_from_regex(user_agent: str) -> str:
    # Order matters: an iPad's UA contains neither "mobile" nor, historically,
    # anything else useful — check tablet first.
    if _TABLET_RE.search(user_agent):
        return DeviceType.TABLET
    if _MOBILE_RE.search(user_agent):
        return DeviceType.MOBILE
    if user_agent:
        return DeviceType.DESKTOP
    return DeviceType.UNKNOWN


__all__ = ["parse", "looks_like_bot"]
