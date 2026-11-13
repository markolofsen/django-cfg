"""ClientIdMiddleware — reads the per-browser id the generated TS SDK sends.

The SDK's request interceptor puts a random id (created once, kept in the
browser's localStorage) in ``X-Client-Id`` on every browser request. This
middleware exposes it as ``request.client_id``.

The id is optional. Requests with no header (server-side rendering, crawlers,
scripts, curl) get ``None``; nothing depends on it being present.

It is a client-supplied hint, not an identity: anyone can send any value. Use
it to group requests (logs, dedupe, rate-limit keys), never to authenticate or
authorize, and never as a replacement for the analytics visitor id.
"""

import re

HEADER_META_KEY = "HTTP_X_CLIENT_ID"
MAX_LENGTH = 64
_VALID = re.compile(r"^[A-Za-z0-9._-]{8,%d}$" % MAX_LENGTH)


def parse_client_id(raw: str) -> str | None:
    """The id if it is well formed, else None (no error: the header is optional)."""
    value = (raw or "").strip()
    return value if _VALID.match(value) else None


class ClientIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.client_id = parse_client_id(request.META.get(HEADER_META_KEY, ""))
        return self.get_response(request)
