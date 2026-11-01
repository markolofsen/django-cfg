"""
OAuth provider configuration.

A provider needs a client id and a secret and nothing else. Scopes, callback
path, state lifetime, endpoints and account linking are constants of the
provider code (``apps.system.accounts.services.oauth``), not knobs.

When ``DjangoConfig.github_oauth`` / ``google_oauth`` is left ``None``, the
settings generator builds the config from the process environment:

    GITHUB_OAUTH__CLIENT_ID / GITHUB_OAUTH__CLIENT_SECRET
    GOOGLE_OAUTH__CLIENT_ID / GOOGLE_OAUTH__CLIENT_SECRET

Both set means the provider is on. An explicit config object wins over env.
"""

from __future__ import annotations

import os
import warnings
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# Env prefix per provider id: ``<PREFIX>__CLIENT_ID`` and ``<PREFIX>__CLIENT_SECRET``.
OAUTH_ENV_PREFIX: Dict[str, str] = {"github": "GITHUB_OAUTH", "google": "GOOGLE_OAUTH"}


class OAuthProviderConfig(BaseModel):
    """Credentials of one OAuth provider."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    # Provider id (``github``); set by subclasses, used for env auto-detect.
    provider_id: ClassVar[str] = ""

    client_id: str = Field(default="", description="OAuth client id")
    client_secret: str = Field(default="", description="OAuth client secret")

    def is_configured(self) -> bool:
        """True when both credentials are set: this is what turns the provider on."""
        return bool(self.client_id and self.client_secret)

    @classmethod
    def env_names(cls) -> tuple[str, str]:
        prefix = OAUTH_ENV_PREFIX[cls.provider_id]
        return f"{prefix}__CLIENT_ID", f"{prefix}__CLIENT_SECRET"

    @classmethod
    def from_env(cls) -> Optional["OAuthProviderConfig"]:
        """Build from ``os.environ``; ``None`` unless both the id and the secret are set."""
        id_name, secret_name = cls.env_names()
        client_id = os.environ.get(id_name, "").strip()
        client_secret = os.environ.get(secret_name, "").strip()
        if client_id and client_secret:
            return cls(client_id=client_id, client_secret=client_secret)
        return None

    def get_info(self) -> Dict[str, Any]:
        """Status for ``show_config``; never includes the secret."""
        return {"configured": self.is_configured(), "client_id": self.client_id}


# Knobs that used to be configurable and are now constants. Accepted for one
# minor release so existing configs keep loading, then rejected.
_DEPRECATED_GITHUB_FIELDS = frozenset({
    "enabled", "scope", "authorize_url", "token_url", "user_api_url",
    "emails_api_url", "callback_path", "state_timeout_seconds",
    "allow_account_linking", "auto_create_user",
})


class GitHubOAuthConfig(OAuthProviderConfig):
    """
    GitHub OAuth app credentials.

    ```python
    github_oauth = GitHubOAuthConfig(client_id="...", client_secret="...")
    ```

    Or set ``GITHUB_OAUTH__CLIENT_ID`` and ``GITHUB_OAUTH__CLIENT_SECRET`` and
    leave ``DjangoConfig.github_oauth`` unset.
    """

    provider_id: ClassVar[str] = "github"

    @model_validator(mode="before")
    @classmethod
    def _drop_deprecated(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        stale = sorted(_DEPRECATED_GITHUB_FIELDS & data.keys())
        if not stale:
            return data
        warnings.warn(
            f"GitHubOAuthConfig: {', '.join(stale)} are no longer configurable and are ignored "
            "(constants now; the provider is on when client_id and client_secret are set, "
            "remove the config object to turn it off). Delete these arguments; "
            "they are rejected in the next minor release.",
            DeprecationWarning,
            stacklevel=2,
        )
        return {k: v for k, v in data.items() if k not in _DEPRECATED_GITHUB_FIELDS}


class GoogleOAuthConfig(OAuthProviderConfig):
    """
    Google OAuth client credentials (Google Cloud "Web application" client).

    ```python
    google_oauth = GoogleOAuthConfig(client_id="...apps.googleusercontent.com", client_secret="...")
    ```

    Or set ``GOOGLE_OAUTH__CLIENT_ID`` and ``GOOGLE_OAUTH__CLIENT_SECRET``.
    """

    provider_id: ClassVar[str] = "google"

    allowed_hosted_domains: List[str] = Field(
        default_factory=list,
        description=(
            "Google Workspace domains allowed to sign in. Empty = any Google account. "
            "Checked against the signed `hd` claim of the ID token."
        ),
    )

    @field_validator("allowed_hosted_domains")
    @classmethod
    def _normalize_domains(cls, v: List[str]) -> List[str]:
        return [d.strip().lower() for d in v if d and d.strip()]


class OAuthConfig(BaseModel):
    """Container for every provider's configuration."""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    github: GitHubOAuthConfig = Field(default_factory=GitHubOAuthConfig)
    google: GoogleOAuthConfig = Field(default_factory=GoogleOAuthConfig)

    def get_enabled_providers(self) -> List[str]:
        """Ids of the providers whose credentials are set."""
        return [pid for pid in ("github", "google") if getattr(self, pid).is_configured()]

    def has_any_provider(self) -> bool:
        return bool(self.get_enabled_providers())


__all__ = [
    "OAUTH_ENV_PREFIX",
    "GitHubOAuthConfig",
    "GoogleOAuthConfig",
    "OAuthConfig",
    "OAuthProviderConfig",
]
