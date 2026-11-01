"""Provider-neutral OAuth types: the identity a provider returns, the errors, the provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, ClassVar, Dict, List, Optional


class OAuthErrorCode(str, Enum):
    """Closed set of error codes on the wire (``error`` in the response body).

    Renaming a value is a breaking change for every generated client.
    """

    OAUTH_DISABLED = "oauth_disabled"
    GITHUB_OAUTH_DISABLED = "github_oauth_disabled"  # GitHub's historical code, kept
    ORIGIN_NOT_ALLOWED = "origin_not_allowed"
    MISSING_REDIRECT_URI = "missing_redirect_uri"
    INVALID_STATE = "invalid_state"
    OAUTH_EXCHANGE_FAILED = "oauth_exchange_failed"
    INVALID_ID_TOKEN = "invalid_id_token"
    EMAIL_MISSING = "email_missing"
    EMAIL_NOT_VERIFIED = "email_not_verified"
    HOSTED_DOMAIN_NOT_ALLOWED = "hosted_domain_not_allowed"
    ACCOUNT_INACTIVE = "account_inactive"
    LINK_NOT_ALLOWED = "link_not_allowed"
    RATE_LIMITED = "rate_limited"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    SERVER_ERROR = "server_error"
    NOT_FOUND = "not_found"  # disconnect: no such connection


def oauth_error_choices() -> List[tuple]:
    """``(value, value)`` pairs of the wire enum.

    The one definition behind both the serializer field and the OpenAPI enum
    name override, so the two hash to the same choice set.
    """
    return [(code.value, code.value) for code in OAuthErrorCode]


HTTP_STATUS: Dict[OAuthErrorCode, int] = {
    OAuthErrorCode.OAUTH_DISABLED: 503,
    OAuthErrorCode.GITHUB_OAUTH_DISABLED: 503,
    OAuthErrorCode.ORIGIN_NOT_ALLOWED: 400,
    OAuthErrorCode.MISSING_REDIRECT_URI: 400,
    OAuthErrorCode.INVALID_STATE: 400,
    OAuthErrorCode.OAUTH_EXCHANGE_FAILED: 400,
    OAuthErrorCode.INVALID_ID_TOKEN: 400,
    OAuthErrorCode.EMAIL_MISSING: 400,
    OAuthErrorCode.EMAIL_NOT_VERIFIED: 400,
    OAuthErrorCode.HOSTED_DOMAIN_NOT_ALLOWED: 403,
    OAuthErrorCode.ACCOUNT_INACTIVE: 403,
    OAuthErrorCode.LINK_NOT_ALLOWED: 403,
    OAuthErrorCode.RATE_LIMITED: 429,
    OAuthErrorCode.PROVIDER_UNAVAILABLE: 502,
    OAuthErrorCode.SERVER_ERROR: 500,
    OAuthErrorCode.NOT_FOUND: 404,
}

# User-safe text per code. Never provider internals.
DESCRIPTIONS: Dict[OAuthErrorCode, str] = {
    OAuthErrorCode.OAUTH_DISABLED: "This sign-in method is not enabled",
    OAuthErrorCode.GITHUB_OAUTH_DISABLED: "GitHub OAuth is not enabled",
    OAuthErrorCode.ORIGIN_NOT_ALLOWED: "This site is not allowed to start sign-in",
    OAuthErrorCode.MISSING_REDIRECT_URI: "redirect_uri not provided and site_url not configured",
    OAuthErrorCode.INVALID_STATE: "Invalid or expired state token",
    OAuthErrorCode.OAUTH_EXCHANGE_FAILED: "The provider rejected the sign-in code",
    OAuthErrorCode.INVALID_ID_TOKEN: "The provider returned an invalid identity token",
    OAuthErrorCode.EMAIL_MISSING: "The provider did not return an email address",
    OAuthErrorCode.EMAIL_NOT_VERIFIED: "The email address is not verified at the provider",
    OAuthErrorCode.HOSTED_DOMAIN_NOT_ALLOWED: "This Google Workspace domain is not allowed",
    OAuthErrorCode.ACCOUNT_INACTIVE: "This account is disabled",
    OAuthErrorCode.LINK_NOT_ALLOWED: "This account cannot be signed in with this provider",
    OAuthErrorCode.RATE_LIMITED: "Too many requests",
    OAuthErrorCode.PROVIDER_UNAVAILABLE: "The provider is temporarily unavailable",
    OAuthErrorCode.SERVER_ERROR: "Authentication failed",
    OAuthErrorCode.NOT_FOUND: "Connection not found",
}


class OAuthError(Exception):
    """A sign-in failure with a wire code. ``description`` is safe to show a user."""

    def __init__(self, code: OAuthErrorCode, description: Optional[str] = None):
        self.code = code
        self.description = description or DESCRIPTIONS[code]
        self.status = HTTP_STATUS[code]
        super().__init__(f"{code.value}: {self.description}")


@dataclass(frozen=True)
class OAuthIdentity:
    """What a provider says about the person. Linking and creation read only this.

    ``provider_user_id`` is the stable key (GitHub numeric id, Google ``sub``).
    ``email`` is empty when the provider gave no usable address; ``email_verified``
    is True only when the provider vouched for it. ``raw`` is stored on the
    connection: it must hold no tokens.
    """

    provider_user_id: str
    email: str = ""
    email_verified: bool = False
    username: str = ""
    name: str = ""
    avatar_url: str = ""
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TokenSet:
    """The token endpoint's answer. ``access_token`` is stored only for providers that need it later."""

    access_token: str = ""
    scopes: List[str] = field(default_factory=list)
    id_token: str = ""


@dataclass(frozen=True)
class ProbeResult:
    ok: bool
    detail: str


class OAuthProvider(ABC):
    """One sign-in provider. Stateless: configuration is read from settings on each call."""

    id: ClassVar[str]
    name: ClassVar[str]
    icon: ClassVar[str]
    authorize_url: ClassVar[str]
    scope: ClassVar[str]
    state_ttl_seconds: ClassVar[int]
    uses_pkce: ClassVar[bool] = False
    uses_nonce: ClassVar[bool] = False
    # GitHub may answer with no verified email; it then signs in under a placeholder address.
    allows_placeholder_email: ClassVar[bool] = False
    placeholder_domain: ClassVar[str] = ""
    disabled_code: ClassVar[OAuthErrorCode] = OAuthErrorCode.OAUTH_DISABLED
    console_url: ClassVar[str] = ""

    def config(self):
        from django.conf import settings

        return getattr(settings, f"{self.id.upper()}_OAUTH_CONFIG", None)

    def is_enabled(self) -> bool:
        config = self.config()
        return config is not None and config.is_configured()

    @abstractmethod
    def build_authorize_params(
        self, *, redirect_uri: str, state: str, code_challenge: str = "", nonce: str = ""
    ) -> Dict[str, str]:
        """Query parameters of the authorization URL."""

    @abstractmethod
    def exchange_code(self, *, code: str, redirect_uri: str, code_verifier: str = "") -> TokenSet:
        """Trade the code for tokens. Raises ``OAuthError`` (exchange failed / provider unavailable)."""

    @abstractmethod
    def fetch_identity(self, tokens: TokenSet, *, nonce: str = "") -> OAuthIdentity:
        """Resolve the person. Raises ``OAuthError``."""

    def check_policy(self, identity: OAuthIdentity) -> None:
        """Provider-specific admission rule (Google: hosted domain). Raises ``OAuthError``."""

    @abstractmethod
    def probe(self) -> ProbeResult:
        """One token-endpoint call with a dummy code: are the client id and secret accepted?"""
