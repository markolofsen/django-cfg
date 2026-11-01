"""GitHub: authorization code flow, identity from ``/user`` and ``/user/emails``."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx

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

TOKEN_URL = "https://github.com/login/oauth/access_token"
USER_URL = "https://api.github.com/user"
EMAILS_URL = "https://api.github.com/user/emails"


class GitHubProvider(OAuthProvider):
    id = "github"
    name = "GitHub"
    icon = "github"
    authorize_url = "https://github.com/login/oauth/authorize"
    scope = "user:email read:user"
    state_ttl_seconds = 300
    allows_placeholder_email = True
    placeholder_domain = "github.local"
    disabled_code = OAuthErrorCode.GITHUB_OAUTH_DISABLED
    console_url = "https://github.com/settings/developers"

    def build_authorize_params(self, *, redirect_uri, state, code_challenge="", nonce=""):
        return {
            "client_id": self.config().client_id,
            "redirect_uri": redirect_uri,
            "scope": self.scope,
            "state": state,
        }

    def _post_token(self, data: Dict[str, str]) -> Dict[str, Any]:
        try:
            with transport.client() as client:
                response = client.post(TOKEN_URL, data=data, headers={"Accept": "application/json"})
        except httpx.HTTPError as exc:
            logger.error("GitHub token endpoint unreachable: %s", type(exc).__name__)
            raise OAuthError(OAuthErrorCode.PROVIDER_UNAVAILABLE) from exc
        if response.status_code >= 500:
            logger.error("GitHub token endpoint answered %s", response.status_code)
            raise OAuthError(OAuthErrorCode.PROVIDER_UNAVAILABLE)
        try:
            body = response.json()
        except ValueError:
            body = {}
        if response.status_code != 200 or not isinstance(body, dict):
            logger.warning("GitHub token exchange failed: HTTP %s", response.status_code)
            raise OAuthError(OAuthErrorCode.OAUTH_EXCHANGE_FAILED)
        return body

    def exchange_code(self, *, code, redirect_uri, code_verifier=""):
        config = self.config()
        body = self._post_token({
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
        })
        if body.get("error") or not body.get("access_token"):
            logger.warning("GitHub token exchange refused: %s", body.get("error"))
            raise OAuthError(OAuthErrorCode.OAUTH_EXCHANGE_FAILED)
        scopes = [s for s in str(body.get("scope", "")).split(",") if s]
        return TokenSet(access_token=body["access_token"], scopes=scopes)

    def fetch_identity(self, tokens, *, nonce=""):
        headers = {
            "Authorization": f"Bearer {tokens.access_token}",
            "Accept": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        try:
            with transport.client() as client:
                user_response = client.get(USER_URL, headers=headers)
                if user_response.status_code >= 500:
                    raise OAuthError(OAuthErrorCode.PROVIDER_UNAVAILABLE)
                if user_response.status_code != 200:
                    logger.warning("GitHub user API answered %s", user_response.status_code)
                    raise OAuthError(OAuthErrorCode.OAUTH_EXCHANGE_FAILED)
                user = user_response.json()
                emails_response = client.get(EMAILS_URL, headers=headers)
                emails = emails_response.json() if emails_response.status_code == 200 else []
        except httpx.HTTPError as exc:
            logger.error("GitHub API unreachable: %s", type(exc).__name__)
            raise OAuthError(OAuthErrorCode.PROVIDER_UNAVAILABLE) from exc
        except ValueError as exc:
            raise OAuthError(OAuthErrorCode.PROVIDER_UNAVAILABLE) from exc

        if not isinstance(user, dict) or user.get("id") is None:
            raise OAuthError(OAuthErrorCode.OAUTH_EXCHANGE_FAILED)

        email = self._verified_email(user.get("email"), emails)
        return OAuthIdentity(
            provider_user_id=str(user["id"]),
            email=email,
            email_verified=bool(email),
            username=(user.get("login") or "").strip(),
            name=(user.get("name") or "").strip(),
            avatar_url=(user.get("avatar_url") or "").strip(),
            raw=user,
        )

    @staticmethod
    def _verified_email(profile_email: Optional[str], emails: Any) -> str:
        """A verified address, or ''. The profile email counts only when ``/user/emails`` lists it as verified."""
        if not isinstance(emails, list):
            return ""
        verified = [e for e in emails if isinstance(e, dict) and e.get("verified") and e.get("email")]
        if profile_email:
            wanted = profile_email.strip().lower()
            for entry in verified:
                if entry["email"].strip().lower() == wanted:
                    return entry["email"]
        for entry in verified:
            if entry.get("primary"):
                return entry["email"]
        return verified[0]["email"] if verified else ""

    def probe(self):
        config = self.config()
        try:
            body = self._post_token({
                "client_id": config.client_id,
                "client_secret": config.client_secret,
                "code": "oauth_check_probe",
            })
        except OAuthError as exc:
            return ProbeResult(False, f"GitHub token endpoint: {exc.code.value}")
        error = body.get("error")
        if error == "bad_verification_code":
            return ProbeResult(True, "bad_verification_code: client id and secret are accepted")
        if error == "incorrect_client_credentials":
            return ProbeResult(False, "incorrect_client_credentials: wrong client id or secret")
        return ProbeResult(False, f"unexpected answer: {error or 'no error field'}")
