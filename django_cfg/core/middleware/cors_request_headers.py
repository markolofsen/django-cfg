"""
CORS preflight header reflection for origins that are already trusted.

django-cors-headers answers a preflight with a fixed Access-Control-Allow-Headers
list. A frontend that sends any other header (X-Holder, Idempotency-Key, ...) is
blocked by the browser with an opaque "CORS error" while the server only sees
OPTIONS 200. This middleware closes that gap without a per-header setting.

Rule: when corsheaders has accepted the origin (the response carries
Access-Control-Allow-Origin), add the headers the preflight asks for
(Access-Control-Request-Headers) to Access-Control-Allow-Headers.

Why this is safe:
- The origin allowlist stays mandatory. An untrusted origin gets no
  Access-Control-Allow-Origin from corsheaders and this middleware leaves the
  response alone.
- A preflight authorizes nothing. Authentication, CSRF and permissions run on the
  real request, so allowing an extra header name only lets a page from a trusted
  origin send it.
- Names are sanitized (HTTP token syntax, count and length caps) and "*" is never
  emitted, so credentialed requests keep working and the browser rule against
  "*" with credentials is not touched.
Starlette (allow_headers=["*"]), Envoy and Spring reflect request headers the same way.

Order in MIDDLEWARE: after PublicAPICORSMiddleware (it answers its public paths with
any origin and never reaches this middleware) and before CorsMiddleware.

Settings:
- CORS_REFLECT_REQUEST_HEADERS (default True): False = strict, static list only.
- CORS_ALLOW_HEADERS: the static list (built from cors_allow_headers + cors_extra_headers).
"""

import logging
import re
from typing import Callable, List, Set, Tuple

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.utils.cache import patch_vary_headers

logger = logging.getLogger(__name__)

# RFC 9110 token. "*" is a token character but means "everything" here, so it is dropped.
_TOKEN = re.compile(r"^[!#$%&'*+\-.^_`|~0-9A-Za-z]+$")
MAX_HEADERS = 64
MAX_NAME_LENGTH = 100
MAX_SEEN = 1024


def parse_requested_headers(raw: str) -> List[str]:
    """Lower-cased, deduplicated, valid header names from an Access-Control-Request-Headers value."""
    names: List[str] = []
    for part in raw.split(","):
        name = part.strip().lower()
        if not name or name == "*" or len(name) > MAX_NAME_LENGTH or not _TOKEN.match(name):
            continue
        if name not in names:
            names.append(name)
        if len(names) >= MAX_HEADERS:
            break
    return names


class CorsRequestHeadersMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response
        self.reflect: bool = getattr(settings, "CORS_REFLECT_REQUEST_HEADERS", True)
        self._seen: Set[Tuple[str, str]] = set()

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        if request.method != "OPTIONS":
            return response
        meta = request.META
        origin = meta.get("HTTP_ORIGIN")
        requested_raw = meta.get("HTTP_ACCESS_CONTROL_REQUEST_HEADERS")
        if not (origin and requested_raw and meta.get("HTTP_ACCESS_CONTROL_REQUEST_METHOD")):
            return response  # not a preflight
        if not response.get("Access-Control-Allow-Origin"):
            return response  # origin not trusted: leave corsheaders' answer as is

        if self.reflect:
            patch_vary_headers(response, ["Access-Control-Request-Headers"])  # the answer depends on it

        allowed_raw = response.get("Access-Control-Allow-Headers", "")
        allowed = [h.strip().lower() for h in allowed_raw.split(",") if h.strip()]
        missing = [n for n in parse_requested_headers(requested_raw) if n not in allowed]
        if not missing:
            return response

        if self.reflect:
            response["Access-Control-Allow-Headers"] = ", ".join(allowed + missing)
            for name in missing:
                self._log_once(
                    origin, name,
                    "CORS preflight from %s: header '%s' not in cors_allow_headers; reflected because "
                    "the origin is trusted (set cors_extra_headers to list it explicitly)",
                    logging.INFO,
                )
        else:
            for name in missing:
                self._log_once(
                    origin, name,
                    "CORS preflight from %s: header '%s' is not allowed; add it to cors_extra_headers",
                    logging.WARNING,
                )
        return response

    def _log_once(self, origin: str, name: str, message: str, level: int) -> None:
        key = (origin, name)
        if key in self._seen:
            return
        if len(self._seen) >= MAX_SEEN:
            self._seen.clear()
        self._seen.add(key)
        logger.log(level, message, origin, name)
