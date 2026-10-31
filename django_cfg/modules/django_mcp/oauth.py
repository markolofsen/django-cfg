"""OAuth 2.1 for an MCP profile: sign in instead of pasting a key.

Claude (web, Desktop), ChatGPT, Claude Code, Codex, Cursor and VS Code all
connect to a remote MCP server by URL and authenticate with OAuth; none of the
web ones can send a custom header. This is the smallest server they accept:

- discovery: RFC 9728 protected-resource and RFC 8414 server metadata;
- RFC 7591 dynamic registration, public clients, PKCE S256 only;
- stateless (one cache entry per spent code makes codes single-use): the client id, the consent request, the code and both tokens are
  signed with ``SECRET_KEY`` (``django.core.signing``), so nothing is stored
  and nothing needs a migration.

THE USER IS IDENTIFIED BY THE PROJECT'S FRONTEND, not here. ``authorize``
validates the request and redirects to ``MCPOAuthConfig.consent_url`` with a
signed ``request``. That page signs the visitor in its usual way (django-cfg
``useAuth``), shows who is connecting, and POSTs the request to
``oauth/approve/`` with the user's own API credentials. The code it gets back
is bound to that user; the access token acts as them.

Redirects are limited to the clients' own callbacks (claude.ai, chatgpt.com,
OpenAI platform, Cursor, vscode.dev) and loopback (Claude Code, Codex, VS
Code), so a stolen client id cannot send a code anywhere else.
"""

from __future__ import annotations

import base64
import calendar
import hashlib
import logging
import re
import time
from typing import Any, Optional
from urllib.parse import urlencode, urlparse

from django.core import signing
from django.http import HttpResponseRedirect, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)

SALT = "django_cfg.mcp.oauth"
REQUEST_TTL = 600
CODE_TTL = 120
MAX_REDIRECTS = 5


# ── signing ──────────────────────────────────────────────────────────────────


def seal(payload: dict, compress: bool = True) -> str:
    return signing.dumps(payload, salt=SALT, compress=compress)


def unseal(token: Optional[str], typ: str) -> Optional[dict]:
    """The payload when the signature, the type and the expiry hold."""
    if not token:
        return None
    try:
        payload = signing.loads(token, salt=SALT)
    except signing.BadSignature:
        return None
    if not isinstance(payload, dict) or payload.get("typ") != typ:
        return None
    exp = payload.get("exp")
    if isinstance(exp, (int, float)) and exp < time.time():
        return None
    return payload


def destination(uri: str) -> str:
    """Where a redirect URI sends the browser, for the consent page: ``host[:port]``, or ``scheme://host`` for a custom scheme."""
    url = urlparse(uri)
    if url.scheme in ("http", "https"):
        return url.netloc.lower()
    return f"{url.scheme}://{url.netloc}".lower()


def _spend_code(code: str) -> bool:
    """True once per code. ``cache.add`` is atomic; a cache that cannot be written refuses (fails safe)."""
    from django.core.cache import cache

    key = "django_cfg.mcp.oauth.code." + hashlib.sha256(code.encode()).hexdigest()
    try:
        return bool(cache.add(key, 1, CODE_TTL + 5))
    except Exception:
        logger.exception("MCP OAuth: code replay guard unavailable; refusing the exchange")
        return False


def challenge_for(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("ascii", "ignore")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


# ── clients ──────────────────────────────────────────────────────────────────

_LOOPBACK = {"localhost", "127.0.0.1", "[::1]", "::1"}


def allowed_redirect(uri: str) -> bool:
    """Only the known clients' callbacks, or the user's own machine."""
    try:
        url = urlparse(uri)
    except ValueError:
        return False
    if url.username or url.password or url.fragment:
        return False
    host = (url.hostname or "").lower()
    if url.scheme == "https":
        if host in ("claude.ai", "claude.com"):
            return url.path == "/api/mcp/auth_callback"
        if host == "chatgpt.com":
            return url.path == "/connector_platform_oauth_redirect" or bool(
                re.fullmatch(r"/connector/oauth/[\w-]+", url.path)
            )
        if host == "platform.openai.com":
            return url.path == "/apps-manage/oauth"
        if host in ("vscode.dev", "insiders.vscode.dev"):
            return url.path == "/redirect"
        return False
    if url.scheme == "http":
        return host in _LOOPBACK
    if url.scheme == "cursor":
        return url.netloc == "anysphere.cursor-mcp"
    return False


def client_from_id(client_id: Optional[str]) -> Optional[dict]:
    return unseal(client_id, "client")


# ── tokens ───────────────────────────────────────────────────────────────────


def key_generation(user_pk: Any) -> int:
    """The user's key generation: ``UserAPIKey.reissued_at`` as integer microseconds.

    0 when the key was never regenerated or the user has no key row. Microseconds,
    not seconds: two regenerations in the same second would otherwise share a
    generation and the older tokens would survive the second one. Costs one query.
    """
    from django_cfg.apps.system.accounts.models import UserAPIKey

    at = UserAPIKey.objects.filter(user_id=user_pk).values_list("reissued_at", flat=True).first()
    if at is None:
        return 0
    return calendar.timegm(at.utctimetuple()) * 1_000_000 + at.microsecond


def token_generation(payload: dict) -> int:
    """A token without ``kg`` (issued before regenerating counted) is generation 0."""
    kg = payload.get("kg")
    return kg if isinstance(kg, int) and not isinstance(kg, bool) and kg > 0 else 0


def issue_tokens(profile, user_pk: Any, client_id: str) -> dict:
    """Both tokens carry the user's key generation (``kg``); regenerating the key outdates them."""
    now = time.time()
    kg = key_generation(user_pk)
    access = seal({"typ": "access", "uid": user_pk, "kg": kg, "prof": profile.name, "exp": now + profile.oauth.access_ttl})
    refresh = seal(
        {"typ": "refresh", "uid": user_pk, "kg": kg, "prof": profile.name, "cid": client_id, "exp": now + profile.oauth.refresh_ttl}
    )
    return {
        "access_token": access,
        "token_type": "Bearer",
        "expires_in": profile.oauth.access_ttl,
        "refresh_token": refresh,
    }


def user_for_access_token(token: str, profile) -> Any:
    """The active user an access token acts as, or ``None``."""
    payload = unseal(token, "access")
    if not payload or payload.get("prof") != getattr(profile, "name", None):
        return None
    return _active_user(payload.get("uid"), payload)


def _active_user(pk: Any, token: Optional[dict] = None) -> Any:
    """The active user; with a ``token`` payload, only if its key generation is still current."""
    from django.contrib.auth import get_user_model

    if pk is None:
        return None
    user = get_user_model().objects.filter(pk=pk, is_active=True).first()
    if user is not None and token is not None and token_generation(token) != key_generation(user.pk):
        return None
    return user


# ── where things live ────────────────────────────────────────────────────────


def issuer(request, profile) -> str:
    configured = profile.oauth.issuer
    if configured:
        return configured.rstrip("/")
    return request.build_absolute_uri("/").rstrip("/")


def resource_url(request, profile) -> str:
    return f"{issuer(request, profile)}/{profile.path.strip('/')}/"


def resource_metadata_url(request, profile) -> str:
    return f"{issuer(request, profile)}/.well-known/oauth-protected-resource/{profile.path.strip('/')}/"


def www_authenticate(request, profile) -> str:
    """The 401 challenge that starts a client's discovery."""
    return f'Bearer resource_metadata="{resource_metadata_url(request, profile)}"'


def _profile(name: Optional[str]):
    from django_cfg.core.state import get_current_config

    config = get_current_config()
    mcp = getattr(config, "mcp", None) if config else None
    profiles = getattr(mcp, "profiles", None) or {}
    if name:
        profile = profiles.get(name)
        return profile if profile is not None and profile.oauth else None
    return next((p for p in profiles.values() if p.oauth), None)


def _json(body: dict, status: int = 200, cache: bool = False) -> JsonResponse:
    response = JsonResponse(body, status=status)
    response["Cache-Control"] = "public, max-age=300" if cache else "no-store"
    response["Access-Control-Allow-Origin"] = "*"
    return response


def _error(error: str, description: str, status: int = 400) -> JsonResponse:
    return _json({"error": error, "error_description": description}, status=status)


class _ProfileView(View):
    profile: Optional[str] = None

    def get_profile(self):
        return _profile(self.profile)

    def options(self, request, *args, **kwargs):
        # Browser-based clients (Claude web, ChatGPT) preflight these.
        response = _json({})
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "content-type, authorization"
        return response


# ── discovery ────────────────────────────────────────────────────────────────


class ProtectedResourceView(_ProfileView):
    """RFC 9728: which authorization server protects this MCP endpoint."""

    def get(self, request, *args, **kwargs):
        profile = self.get_profile()
        if profile is None:
            return _error("not_found", "No OAuth-enabled MCP profile.", status=404)
        return _json(
            {
                "resource": resource_url(request, profile),
                "authorization_servers": [issuer(request, profile)],
                "bearer_methods_supported": ["header"],
            },
            cache=True,
        )


class AuthorizationServerView(_ProfileView):
    """RFC 8414: where to register, authorize and fetch tokens."""

    def get(self, request, *args, **kwargs):
        profile = self.get_profile()
        if profile is None:
            return _error("not_found", "No OAuth-enabled MCP profile.", status=404)
        base = resource_url(request, profile)
        return _json(
            {
                "issuer": issuer(request, profile),
                "authorization_endpoint": f"{base}oauth/authorize/",
                "token_endpoint": f"{base}oauth/token/",
                "registration_endpoint": f"{base}oauth/register/",
                "response_types_supported": ["code"],
                "grant_types_supported": ["authorization_code", "refresh_token"],
                "code_challenge_methods_supported": ["S256"],
                "token_endpoint_auth_methods_supported": ["none"],
                # RFC 9207: every authorization response carries `iss`. It is
                # NOT advertised: Codex then insists on `iss` yet drops it from
                # its loopback callback ("response missing required issuer"),
                # so the flag would only lock that client out.
            },
            cache=True,
        )


# ── registration, authorization, tokens ─────────────────────────────────────


def _body(request) -> dict:
    import json

    if "json" in (request.content_type or ""):
        try:
            data = json.loads(request.body or b"{}")
        except ValueError:
            return {}
        return data if isinstance(data, dict) else {}
    return {k: v for k, v in request.POST.items()}


@method_decorator(csrf_exempt, name="dispatch")
class RegisterView(_ProfileView):
    """RFC 7591 for public clients. Nothing is stored: the id is signed."""

    def post(self, request, *args, **kwargs):
        if self.get_profile() is None:
            return _error("not_found", "No OAuth-enabled MCP profile.", status=404)
        body = _body(request)
        uris = body.get("redirect_uris")
        if not isinstance(uris, list) or not uris or not all(isinstance(u, str) for u in uris):
            return _error("invalid_client_metadata", "redirect_uris is required.")
        if len(uris) > MAX_REDIRECTS or not all(allowed_redirect(u) for u in uris):
            return _error("invalid_redirect_uri", "redirect_uris must be a known client's callback or loopback.")
        name = body.get("client_name") if isinstance(body.get("client_name"), str) else "MCP client"
        name = name[:80]
        client_id = seal({"typ": "client", "uris": uris, "name": name})
        return _json(
            {
                "client_id": client_id,
                "client_name": name,
                "redirect_uris": uris,
                "grant_types": ["authorization_code", "refresh_token"],
                "response_types": ["code"],
                "token_endpoint_auth_method": "none",
            },
            status=201,
        )


class AuthorizeView(_ProfileView):
    """Validate the request and hand it, signed, to the project's consent page."""

    def get(self, request, *args, **kwargs):
        profile = self.get_profile()
        if profile is None:
            return _error("not_found", "No OAuth-enabled MCP profile.", status=404)
        q = request.GET
        client = client_from_id(q.get("client_id"))
        uris = (client or {}).get("uris") or []
        redirect_uri = q.get("redirect_uri") or (uris[0] if uris else "")
        challenge = q.get("code_challenge") or ""
        if not (
            client
            and redirect_uri in uris
            and q.get("response_type") == "code"
            and q.get("code_challenge_method") == "S256"
            and len(challenge) >= 43
        ):
            return _error("invalid_request", "Unknown client, redirect_uri, or PKCE S256 missing.")
        # Not compressed, so the consent page can read `name` and `dest` for display
        # (base64 JSON before the first ":"). Safe: the page only DISPLAYS them; the
        # grant is made by /oauth/approve/, which verifies this same signature and uses
        # its own `uri`. Editing the display breaks the signature, so a forged display
        # cannot ride on a genuine grant, and a genuine request always shows its real
        # destination (`dest` is derived from the validated `uri` right here).
        consent = seal(
            {
                "typ": "request",
                "cid": q.get("client_id"),
                "name": client.get("name") or "MCP client",
                "uri": redirect_uri,
                "dest": destination(redirect_uri),
                "ch": challenge,
                "st": q.get("state") or "",
                "prof": profile.name,
                "iss": issuer(request, profile),
                "exp": time.time() + REQUEST_TTL,
            },
            compress=False,
        )
        consent_url = consent_page(profile.oauth)
        target = f"{consent_url}{'&' if '?' in consent_url else '?'}"
        target += urlencode({"request": consent, "client": client.get("name") or "MCP client"})
        return HttpResponseRedirect(target)


def consent_page(oauth) -> str:
    """The page that approves a request: the configured URL, else the host's Settings dialog."""
    if oauth.consent_url:
        return oauth.consent_url
    from django_cfg.core.state import get_current_config

    config = get_current_config()
    site = config.site_url if config else "http://localhost:3000"
    return f"{site.rstrip('/')}/#settings/mcp"


def _with_params(uri: str, params: dict) -> str:
    return f"{uri}{'&' if '?' in uri else '?'}{urlencode({k: v for k, v in params.items() if v})}"


@extend_schema(exclude=True)
class ApproveView(APIView):
    """The consent page posts here with the signed-in user's own credentials.

    Body ``{"request": <from authorize>, "allow": true|false}``. Answers
    ``{"redirect_to": <client callback>}``: with a code bound to this user, or
    with ``error=access_denied``. The page navigates there.
    """

    permission_classes = [IsAuthenticated]
    profile: Optional[str] = None

    def post(self, request, *args, **kwargs):
        payload = unseal(request.data.get("request"), "request")
        profile = _profile(payload.get("prof")) if payload else None
        if not payload or profile is None:
            return Response(
                {"error": "invalid_request", "error_description": "The request expired or is not valid. Start again."},
                status=400,
            )
        if request.data.get("allow") is False:
            target = _with_params(payload["uri"], {"error": "access_denied", "state": payload["st"], "iss": payload["iss"]})
            return Response({"redirect_to": target})
        code = seal(
            {
                "typ": "code",
                "cid": payload["cid"],
                "uri": payload["uri"],
                "ch": payload["ch"],
                "uid": request.user.pk,
                "prof": profile.name,
                "exp": time.time() + CODE_TTL,
            }
        )
        logger.info("MCP OAuth: user %s allowed %r", request.user.pk, payload.get("name"))
        target = _with_params(payload["uri"], {"code": code, "state": payload["st"], "iss": payload["iss"]})
        return Response({"redirect_to": target})


@method_decorator(csrf_exempt, name="dispatch")
class TokenView(_ProfileView):
    def post(self, request, *args, **kwargs):
        profile = self.get_profile()
        if profile is None:
            return _error("not_found", "No OAuth-enabled MCP profile.", status=404)
        body = _body(request)

        def get(key: str) -> str:
            value = body.get(key)
            return value if isinstance(value, str) else ""

        grant = get("grant_type")

        if grant == "authorization_code":
            code = unseal(get("code"), "code")
            if not code or code.get("prof") != profile.name or code.get("cid") != get("client_id"):
                return _error("invalid_grant", "The code is not valid or has expired.")
            if get("redirect_uri") and get("redirect_uri") != code.get("uri"):
                return _error("invalid_grant", "redirect_uri does not match.")
            if challenge_for(get("code_verifier")) != code.get("ch"):
                return _error("invalid_grant", "PKCE verification failed.")
            if _active_user(code.get("uid")) is None:
                return _error("invalid_grant", "The account is not active.")
            # Single use. Spent only after PKCE passed, so nobody without the verifier can burn it.
            # Refresh tokens are not rotated: they are bound to the key generation, and Renew key revokes them.
            if not _spend_code(get("code")):
                return _error("invalid_grant", "The code was already used.")
            return _json(issue_tokens(profile, code["uid"], code["cid"]))

        if grant == "refresh_token":
            refresh = unseal(get("refresh_token"), "refresh")
            if not refresh or refresh.get("prof") != profile.name or not client_from_id(refresh.get("cid")):
                return _error("invalid_grant", "The refresh token is not valid.")
            if _active_user(refresh.get("uid"), refresh) is None:
                return _error("invalid_grant", "The account is not active.")
            return _json(issue_tokens(profile, refresh["uid"], refresh["cid"]))

        return _error("unsupported_grant_type", "Use authorization_code or refresh_token.")

