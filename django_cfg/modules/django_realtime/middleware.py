"""`X-Realtime-Cid` -> `publishing.current_cid` for the request, so a client is not sent its own change back.

Installed by django-cfg when `realtime.enabled`. The header is a claim, checked when a publish reads it
(`publishing.sender_cid()`): by then DRF has authenticated the request (a bearer token is invisible to middleware),
and the id must verify for that user, or for the client IP of a visitor (`auth.verify_cid`). Anything else is ignored.
"""

from __future__ import annotations

from typing import Optional

from .protocol import CID_RE
from .publishing import current_cid


class CidClaim:
    """An unverified `X-Realtime-Cid` and the request it came with."""

    __slots__ = ("request", "value")

    def __init__(self, request, value: str) -> None:
        self.request = request
        self.value = value

    def resolve(self) -> Optional[str]:
        from .auth import cid_subject, verify_cid

        user = getattr(self.request, "user", None)
        authenticated = bool(getattr(user, "is_authenticated", False))
        subject = cid_subject(authenticated, getattr(user, "pk", None), self.request.META.get("REMOTE_ADDR", ""))
        return self.value if verify_cid(self.value, subject) else None


class RealtimeCidMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        value = request.META.get("HTTP_X_REALTIME_CID", "")
        token = current_cid.set(CidClaim(request, value) if CID_RE.match(value) else None)
        try:
            return self.get_response(request)
        finally:
            current_cid.reset(token)
