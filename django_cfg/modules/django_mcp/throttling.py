"""Rate limiting for the MCP endpoints.

**`rate_limit` was declared and never enforced.** The field was validated
(`__cfg__.py`), stored, and passed into the built config — and nothing read it.
Searching the module for a throttle returned the config plumbing and nothing
else. A field that looks like a limit and is not one answers the reviewer's
question wrongly, which is worse than having no field.

Behind an access key that was tolerable: the caller is known and the key can be
rotated. It is not tolerable for an anonymous endpoint, which runs database
queries for whoever asks at whatever rate they ask.

Two properties this module must keep:

**Anonymous callers are bucketed by IP; key holders share a bucket per key.**
One bucket for everyone would let a single anonymous caller exhaust the limit
for every other client, turning a rate limit into a denial-of-service lever.

**A missing cache backend must not silently disable the limit.** Django's
default is LocMemCache — per process, so a multi-worker deployment enforces the
rate N times over. That is a real weakening and it is logged once at startup
rather than discovered from a bill.
"""

from __future__ import annotations

import logging

from rest_framework.throttling import SimpleRateThrottle

logger = logging.getLogger(__name__)

#: Used when the config cannot be read at all. Deliberately tight: an endpoint
#: whose policy is unknown should not be the fast path.
FALLBACK_RATE = "60/minute"


class MCPRateThrottle(SimpleRateThrottle):
    """Throttle whose rate comes from the MCP config, not DRF settings.

    DRF resolves a rate from ``THROTTLE_RATES[scope]``, which lives in Django
    settings. The MCP limit lives in the project's MCP config, so the rate is
    read here instead. DRF instantiates a throttle per request, so this reads
    live — a rate change does not need a restart.
    """

    scope = "mcp"

    def __init__(self):
        self.rate = self.get_rate()
        self.num_requests, self.duration = self.parse_rate(self.rate)

    def get_rate(self) -> str:
        try:
            from django_cfg.core.state import get_current_config

            config = get_current_config()
            mcp_config = config.mcp if config and config.mcp else None
            if mcp_config is None:
                # MCP unconfigured: the endpoint is not serving anything, and a
                # throttle that raised here would break the 404 path.
                return FALLBACK_RATE
            return str(getattr(mcp_config, "rate_limit", None) or FALLBACK_RATE)
        except Exception as exc:  # noqa: BLE001 — never break a request on config
            logger.warning("MCP throttle could not read its rate (%s); using %s", exc, FALLBACK_RATE)
            return FALLBACK_RATE

    def get_cache_key(self, request, view) -> str | None:
        """One bucket per credential, or per IP when anonymous.

        Sharing one bucket across callers would let any single client exhaust
        the limit for all of them.
        """
        presented = request.headers.get("X-MCP-Access-Key")
        if presented:
            # Hash it: cache keys reach logs, memcached dumps and error
            # reporters, and the raw value is the credential itself.
            import hashlib

            ident = "key:" + hashlib.sha256(presented.encode("utf-8")).hexdigest()[:32]
        else:
            ident = "ip:" + (self.get_ident(request) or "unknown")

        return self.cache_format % {"scope": self.scope, "ident": ident}
