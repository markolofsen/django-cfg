"""Google: OpenID Connect authorization code flow with PKCE (S256) and a nonce.

Identity comes from the ID token returned by the token endpoint. The signature
is verified against Google's JWKS even though the token arrives over TLS from
Google itself; every failure closes (no unverified fallback).
"""

from __future__ import annotations

import hmac
import logging
import threading
import time
from typing import Any, Dict, Optional

import httpx
import jwt

from . import transport
from .base import (
    OAuthError,
    OAuthErrorCode,
    OAuthIdentity,
    OAuthProvider,
    ProbeResult,
    TokenSet,
)

logger = logging.getLogger(__name__)

TOKEN_URL = "https://oauth2.googleapis.com/token"
JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"
ISSUERS = ("https://accounts.google.com", "accounts.google.com")
LEEWAY_SECONDS = 30
JWKS_TTL_SECONDS = 3600
# An unknown `kid` triggers at most one refetch per this window (forged kids must not hammer Google).
JWKS_MIN_REFETCH_SECONDS = 60
MAX_SUB_LENGTH = 255


class _JWKSCache:
    """Process-local cache of Google's signing keys by ``kid``."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._keys: Dict[str, jwt.PyJWK] = {}
        self._fetched_at = 0.0

    def reset(self) -> None:
        with self._lock:
            self._keys, self._fetched_at = {}, 0.0

    def get(self, kid: str) -> Optional[jwt.PyJWK]:
        """The key for ``kid``; None when Google does not publish it. Raises ``provider_unavailable``."""
        with self._lock:
            now = time.monotonic()
            fresh = bool(self._keys) and now - self._fetched_at < JWKS_TTL_SECONDS
            if fresh and kid in self._keys:
                return self._keys[kid]
            if fresh and now - self._fetched_at < JWKS_MIN_REFETCH_SECONDS:
                return None  # just fetched; this kid is not published
            self._keys = self._fetch()
            self._fetched_at = now
            return self._keys.get(kid)

    @staticmethod
    def _fetch() -> Dict[str, jwt.PyJWK]:
        try:
            with transport.client() as client:
                response = client.get(JWKS_URL)
            if response.status_code != 200:
                raise ValueError(f"HTTP {response.status_code}")
            entries = response.json()["keys"]
            keys = {}
            for entry in entries:
                if entry.get("kty") == "RSA" and entry.get("kid") and entry.get("use", "sig") == "sig":
                    keys[entry["kid"]] = jwt.PyJWK.from_dict(entry, algorithm="RS256")
        except (httpx.HTTPError, ValueError, KeyError, TypeError, jwt.PyJWTError) as exc:
            logger.error("Google JWKS fetch failed: %s", type(exc).__name__)
            raise OAuthError(OAuthErrorCode.PROVIDER_UNAVAILABLE) from exc
        if not keys:
            logger.error("Google JWKS fetch returned no usable keys")
            raise OAuthError(OAuthErrorCode.PROVIDER_UNAVAILABLE)
        return keys


_jwks = _JWKSCache()


def reset_jwks_cache() -> None:
    _jwks.reset()


class GoogleProvider(OAuthProvider):
    id = "google"
    name = "Google"
    icon = "google"
    authorize_url = "https://accounts.google.com/o/oauth2/v2/auth"
    scope = "openid email profile"
    state_ttl_seconds = 600
    uses_pkce = True
    uses_nonce = True
    console_url = "https://console.cloud.google.com/auth/clients"

    def build_authorize_params(self, *, redirect_uri, state, code_challenge="", nonce=""):
        config = self.config()
        params = {
            "client_id": config.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": self.scope,
            "state": state,
            "nonce": nonce,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "prompt": "select_account",
        }
        if len(config.allowed_hosted_domains) == 1:
            params["hd"] = config.allowed_hosted_domains[0]  # UX hint only; `hd` is enforced on the token
        return params

    def _post_token(self, data: Dict[str, str]) -> Dict[str, Any]:
        try:
            with transport.client() as client:
                response = client.post(TOKEN_URL, data=data)
        except httpx.HTTPError as exc:
            logger.error("Google token endpoint unreachable: %s", type(exc).__name__)
            raise OAuthError(OAuthErrorCode.PROVIDER_UNAVAILABLE) from exc
        try:
            body = response.json()
        except ValueError:
            body = {}
        if not isinstance(body, dict):
            body = {}
        if response.status_code >= 500:
            logger.error("Google token endpoint answered %s", response.status_code)
            raise OAuthError(OAuthErrorCode.PROVIDER_UNAVAILABLE)
        if response.status_code != 200:
            logger.warning("Google token exchange refused: %s", body.get("error", response.status_code))
            raise OAuthError(OAuthErrorCode.OAUTH_EXCHANGE_FAILED)
        return body

    def exchange_code(self, *, code, redirect_uri, code_verifier=""):
        config = self.config()
        body = self._post_token({
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "code_verifier": code_verifier,
        })
        return TokenSet(
            access_token="",  # nothing calls a Google API after sign-in: do not keep the token
            scopes=str(body.get("scope", "")).split(),
            id_token=str(body.get("id_token") or ""),
        )

    def fetch_identity(self, tokens, *, nonce=""):
        if not tokens.id_token:
            raise OAuthError(OAuthErrorCode.INVALID_ID_TOKEN)
        claims = self._verify_id_token(tokens.id_token)
        if not nonce or not hmac.compare_digest(str(claims.get("nonce", "")).encode(), nonce.encode()):
            logger.warning("Google ID token nonce mismatch")
            raise OAuthError(OAuthErrorCode.INVALID_ID_TOKEN)

        picture = str(claims.get("picture") or "")
        return OAuthIdentity(
            provider_user_id=claims["sub"],
            email=str(claims.get("email") or "").strip(),
            email_verified=claims.get("email_verified") is True or claims.get("email_verified") == "true",
            name=str(claims.get("name") or "").strip(),
            avatar_url=picture if picture.startswith("https://") and len(picture) <= 500 else "",
            raw={k: v for k, v in claims.items() if k not in ("nonce", "at_hash")},
        )

    def _verify_id_token(self, id_token: str) -> Dict[str, Any]:
        client_id = self.config().client_id
        try:
            header = jwt.get_unverified_header(id_token)
        except jwt.PyJWTError as exc:
            raise OAuthError(OAuthErrorCode.INVALID_ID_TOKEN) from exc
        kid = header.get("kid")
        if header.get("alg") != "RS256" or not isinstance(kid, str) or not kid:
            logger.warning("Google ID token rejected: alg=%r kid=%r", header.get("alg"), kid)
            raise OAuthError(OAuthErrorCode.INVALID_ID_TOKEN)

        key = _jwks.get(kid)
        if key is None:
            logger.warning("Google ID token rejected: unknown kid")
            raise OAuthError(OAuthErrorCode.INVALID_ID_TOKEN)

        try:
            claims = jwt.decode(
                id_token,
                key=key,
                algorithms=["RS256"],
                audience=client_id,
                issuer=ISSUERS,
                leeway=LEEWAY_SECONDS,
                options={"require": ["exp", "iat", "iss", "aud", "sub"]},
            )
        except jwt.PyJWTError as exc:
            logger.warning("Google ID token rejected: %s", type(exc).__name__)
            raise OAuthError(OAuthErrorCode.INVALID_ID_TOKEN) from exc

        azp = claims.get("azp")
        audience = claims["aud"]
        if (azp is not None and azp != client_id) or (isinstance(audience, list) and len(audience) > 1 and azp is None):
            logger.warning("Google ID token rejected: azp")
            raise OAuthError(OAuthErrorCode.INVALID_ID_TOKEN)

        sub = claims["sub"]
        if not isinstance(sub, str) or not sub or len(sub) > MAX_SUB_LENGTH or not sub.isascii():
            logger.warning("Google ID token rejected: sub")
            raise OAuthError(OAuthErrorCode.INVALID_ID_TOKEN)
        return claims

    def check_policy(self, identity):
        allowed = self.config().allowed_hosted_domains
        if allowed and str(identity.raw.get("hd") or "").lower() not in allowed:
            raise OAuthError(OAuthErrorCode.HOSTED_DOMAIN_NOT_ALLOWED)

    def probe(self):
        config = self.config()
        try:
            with transport.client() as client:
                response = client.post(TOKEN_URL, data={
                    "grant_type": "authorization_code",
                    "code": "oauth_check_probe",
                    "redirect_uri": "https://example.com/auth?provider=google",
                    "client_id": config.client_id,
                    "client_secret": config.client_secret,
                    "code_verifier": "x" * 43,
                })
            error = response.json().get("error", "")
        except (httpx.HTTPError, ValueError, AttributeError):
            return ProbeResult(False, "Google token endpoint unreachable")
        if error == "invalid_grant":
            return ProbeResult(True, "invalid_grant: client id and secret are accepted")
        if error == "invalid_client":
            return ProbeResult(False, "invalid_client: wrong client id or secret")
        return ProbeResult(False, f"unexpected answer: {error or response.status_code}")
