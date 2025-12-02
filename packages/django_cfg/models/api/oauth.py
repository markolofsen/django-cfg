"""
OAuth Configuration for Django CFG
Type-safe OAuth provider configuration with Pydantic v2
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class GitHubOAuthConfig(BaseModel):
    """
    GitHub OAuth Configuration

    Type-safe GitHub OAuth settings for social authentication.
    Follows Django-CFG configuration patterns.

    Example:
        ```python
        github_oauth = GitHubOAuthConfig(
            enabled=True,
            client_id="your_client_id",
            client_secret="your_client_secret",
        )
        ```
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    # === Enable/Disable ===
    enabled: bool = Field(
        default=False,
        description="Enable GitHub OAuth authentication"
    )

    # === Credentials ===
    client_id: str = Field(
        default="",
        description="GitHub OAuth App Client ID"
    )

    client_secret: str = Field(
        default="",
        description="GitHub OAuth App Client Secret"
    )

    # === OAuth Scopes ===
    scope: List[str] = Field(
        default=["user:email", "read:user"],
        description="OAuth scopes to request from GitHub"
    )

    # === GitHub OAuth Endpoints (rarely need customization) ===
    authorize_url: str = Field(
        default="https://github.com/login/oauth/authorize",
        description="GitHub OAuth authorization URL"
    )

    token_url: str = Field(
        default="https://github.com/login/oauth/access_token",
        description="GitHub OAuth token exchange URL"
    )

    user_api_url: str = Field(
        default="https://api.github.com/user",
        description="GitHub API URL for user info"
    )

    emails_api_url: str = Field(
        default="https://api.github.com/user/emails",
        description="GitHub API URL for user emails"
    )

    # === Callback Configuration ===
    callback_path: str = Field(
        default="/auth",
        description="Frontend OAuth callback path (appended to site_url to form redirect_uri)"
    )

    # === Security Settings ===
    state_timeout_seconds: int = Field(
        default=300,
        ge=60,
        le=600,
        description="State token timeout in seconds (for CSRF protection)"
    )

    allow_account_linking: bool = Field(
        default=True,
        description="Allow linking GitHub to existing accounts with same email"
    )

    auto_create_user: bool = Field(
        default=True,
        description="Automatically create new user if not found"
    )

    @field_validator("scope")
    @classmethod
    def validate_scope(cls, v: List[str]) -> List[str]:
        """Ensure user:email scope is always included."""
        if "user:email" not in v:
            v = ["user:email"] + v
        return v

    @field_validator("client_id", "client_secret")
    @classmethod
    def validate_credentials(cls, v: str) -> str:
        """Strip whitespace from credentials."""
        return v.strip()

    def is_configured(self) -> bool:
        """
        Check if GitHub OAuth is properly configured.

        Returns:
            True if enabled and credentials are set
        """
        return bool(self.enabled and self.client_id and self.client_secret)

    def get_scope_string(self) -> str:
        """
        Get scope as space-separated string.

        Returns:
            Scopes joined by space (GitHub format)
        """
        return " ".join(self.scope)

    def get_redirect_uri(self, provider: str = "github") -> Optional[str]:
        """
        Get full redirect URI using site_url from config.

        Args:
            provider: OAuth provider name (default: "github")

        Returns:
            Full redirect URI or None if config not available
            Example: https://myapp.com/auth?provider=github
        """
        try:
            from django_cfg.core import get_current_config
            config = get_current_config()
            if config and hasattr(config, 'site_url') and config.site_url:
                base_url = config.site_url.rstrip('/')
                path = self.callback_path.lstrip('/')
                return f"{base_url}/{path}?provider={provider}"
        except Exception:
            pass
        return None

    def get_info(self) -> Dict[str, Any]:
        """
        Get human-readable configuration info.

        Returns:
            Dictionary with configuration status
        """
        return {
            "enabled": self.enabled,
            "configured": self.is_configured(),
            "scopes": self.scope,
            "allow_account_linking": self.allow_account_linking,
            "auto_create_user": self.auto_create_user,
            "callback_path": self.callback_path,
            "redirect_uri": self.get_redirect_uri(),
        }


class OAuthConfig(BaseModel):
    """
    Aggregated OAuth Configuration

    Container for all OAuth provider configurations.
    Extensible for future providers (Google, GitLab, etc.)
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    github: GitHubOAuthConfig = Field(
        default_factory=GitHubOAuthConfig,
        description="GitHub OAuth configuration"
    )

    # Future providers:
    # google: GoogleOAuthConfig = Field(default_factory=GoogleOAuthConfig)
    # gitlab: GitLabOAuthConfig = Field(default_factory=GitLabOAuthConfig)

    def get_enabled_providers(self) -> List[str]:
        """
        Get list of enabled OAuth providers.

        Returns:
            List of provider names that are enabled and configured
        """
        providers = []
        if self.github.is_configured():
            providers.append("github")
        return providers

    def has_any_provider(self) -> bool:
        """
        Check if any OAuth provider is configured.

        Returns:
            True if at least one provider is enabled and configured
        """
        return len(self.get_enabled_providers()) > 0


# Export
__all__ = [
    "GitHubOAuthConfig",
    "OAuthConfig",
]
