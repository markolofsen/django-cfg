"""Handshake identity and origin: the scope becomes an `HttpRequest`, the project's DRF authenticators decide.

`authenticate()` is sync and may touch the ORM (sessions, users, API keys); the connection runs it in the hook
pool. It reads `REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"]` at call time, so `override_settings` works.
A bearer token from the `auth` frame is presented as `Authorization: Bearer <token>`, exactly as over HTTP.

Origin: browsers always send `Origin` on a WebSocket handshake, and a cookie-authenticated socket opened from a
foreign page is cross-site WebSocket hijacking. So the origin must be the same origin (with a `Host` that
`ALLOWED_HOSTS` accepts), a `CSRF_TRUSTED_ORIGINS` entry or a `RealtimeConfig.allowed_origins` entry. A host merely
listed in `ALLOWED_HOSTS` is not a trusted origin. A handshake with no `Origin` is a non-browser client and is
allowed only when it carries no cookie.

Connection ids: `hello.cid` is a random half plus an HMAC (SECRET_KEY) of that half and the socket's subject (the
user, or the client IP for a visitor). `X-Realtime-Cid` is honoured only when it verifies for the request's own
subject, so one user cannot mute another's socket by sending its id.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Optional, Union
from urllib.parse import urlsplit

from django_cfg.core.edge import bind_edge, meta_from_scope

from .publishing import session_hash

if TYPE_CHECKING:
    from django.http import HttpRequest

    from django_cfg.models.django.realtime import RealtimeConfig


class AuthFailed(Exception):
    """Credentials were presented and refused (close 4419: the client refreshes them and reconnects)."""


@dataclass(frozen=True)
class Identity:
    """Who the socket belongs to; built in the hook thread so nothing lazy reaches the event loop."""

    user: Any
    user_id: Union[int, str, None]
    is_authenticated: bool
    client_ip: str
    token: Optional[str] = None     # the `auth` frame's token, kept for the periodic re-check
    session: Optional[str] = None   # hash of the session key the handshake carried (kicks by session)

    @property
    def limit_key(self) -> str:
        return f"user:{self.user_id}" if self.is_authenticated else f"ip:{self.client_ip}"

    def matches_kick(self, kick) -> bool:
        if not self.is_authenticated:
            return False
        if kick.get("all"):
            return True
        if "user" in kick:
            return str(kick["user"]) == str(self.user_id)
        return bool(self.session) and kick.get("session") == self.session


def cid_subject(is_authenticated: bool, user_id: Any, client_ip: str) -> str:
    return f"u:{user_id}" if is_authenticated else f"ip:{client_ip}"


def _cid_mac(nonce: str, subject: str) -> str:
    from django.utils.crypto import salted_hmac

    return salted_hmac("django_cfg.realtime.cid", f"{nonce}|{subject}").hexdigest()[:16]


def issue_cid(identity: Identity) -> str:
    """A connection id bound to the identity: 16 random hex + 16 hex of HMAC(nonce, subject)."""
    import secrets

    nonce = secrets.token_hex(8)
    return nonce + _cid_mac(nonce, cid_subject(identity.is_authenticated, identity.user_id, identity.client_ip))


def verify_cid(value: str, subject: str) -> bool:
    import hmac

    if not isinstance(value, str) or len(value) != 32:
        return False
    nonce, mac = value[:16], value[16:]
    return hmac.compare_digest(mac, _cid_mac(nonce, subject))


def build_request(scope, token: Optional[str] = None) -> "HttpRequest":
    """An `HttpRequest` for the handshake: headers, cookies, client address through the edge rules."""
    from django.http import HttpRequest
    from django.http.cookie import parse_cookie

    meta = meta_from_scope(scope)
    meta["REQUEST_METHOD"] = "GET"
    if token:
        meta["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    request = HttpRequest()
    request.method = "GET"
    request.META = meta
    request.path = request.path_info = scope.get("path", "/")
    request.COOKIES = parse_cookie(meta.get("HTTP_COOKIE", ""))
    bind_edge(request)
    return request


def _attach_session_user(request: "HttpRequest") -> None:
    """What SessionMiddleware and AuthenticationMiddleware would do, so SessionAuthentication sees the user."""
    from django.apps import apps
    from django.conf import settings

    if apps.is_installed("django.contrib.sessions"):
        from importlib import import_module

        engine = import_module(settings.SESSION_ENGINE)
        request.session = engine.SessionStore(request.COOKIES.get(settings.SESSION_COOKIE_NAME))
    if apps.is_installed("django.contrib.auth"):
        from django.contrib.auth import get_user
        from django.contrib.auth.models import AnonymousUser

        request.user = get_user(request) if hasattr(request, "session") else AnonymousUser()


def authenticate(scope, token: Optional[str] = None) -> Identity:
    """Run the project's DRF authenticators on the handshake. Sync; may use the ORM. AuthFailed on refusal."""
    from rest_framework.exceptions import APIException
    from rest_framework.request import Request
    from rest_framework.settings import api_settings

    request = build_request(scope, token)
    _attach_session_user(request)
    drf = Request(request, authenticators=[cls() for cls in api_settings.DEFAULT_AUTHENTICATION_CLASSES])
    try:
        user = drf.user
    except APIException as exc:
        raise AuthFailed(str(getattr(exc, "detail", exc))) from exc
    authenticated = bool(user is not None and getattr(user, "is_authenticated", False))
    if token and not authenticated:
        raise AuthFailed("the token did not authenticate")
    session = getattr(request, "session", None)
    session_key = getattr(session, "session_key", None) if session is not None else None
    return Identity(
        user=user,
        user_id=user.pk if authenticated else None,
        is_authenticated=authenticated,
        client_ip=request.META.get("REMOTE_ADDR", ""),
        token=token,
        session=session_hash(session_key) if session_key else None,
    )


# ---------------------------------------------------------------- origin

def _origin_matches(origin: str, trusted: str) -> bool:
    """Django's CSRF_TRUSTED_ORIGINS rule: exact origin, or `scheme://*.domain` for subdomains."""
    o, t = urlsplit(origin), urlsplit(trusted.rstrip("/"))
    if o.scheme != t.scheme:
        return False
    if t.netloc.startswith("*."):
        return o.netloc == t.netloc[2:] or o.netloc.endswith(t.netloc[1:])
    return o.netloc == t.netloc


def _allowed_hosts() -> list:
    """Hosts a same-origin handshake's `Host` header may name."""
    from django.conf import settings

    hosts = list(settings.ALLOWED_HOSTS)
    if settings.DEBUG and not hosts:
        hosts = [".localhost", "127.0.0.1", "[::1]"]
    return hosts


def origin_allowed(meta, config: "RealtimeConfig") -> bool:
    """True when the handshake may proceed; see the module docstring."""
    from django.conf import settings
    from django.http.request import split_domain_port, validate_host

    origin = meta.get("HTTP_ORIGIN")
    if not origin:
        return not meta.get("HTTP_COOKIE")
    if origin == "null":
        return False
    parts = urlsplit(origin)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        return False
    hosts = _allowed_hosts()
    host_header = (meta.get("HTTP_HOST") or "").lower()
    if host_header and parts.netloc.lower() == host_header:
        domain, _port = split_domain_port(host_header)
        if domain and validate_host(domain, hosts):
            return True
    trusted = [*getattr(settings, "CSRF_TRUSTED_ORIGINS", []), *config.allowed_origins]
    return any(_origin_matches(origin, t) for t in trusted)


__all__ = [
    "AuthFailed", "Identity", "authenticate", "build_request", "cid_subject", "issue_cid", "origin_allowed",
    "verify_cid",
]
