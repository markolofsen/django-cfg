"""
OAuth settings generator.

Emits ``<PROVIDER>_OAUTH_CONFIG`` for every provider that has credentials: the
explicit ``DjangoConfig.<provider>_oauth`` object, else one built from the
process environment (``GITHUB_OAUTH__CLIENT_ID`` ... see ``models.api.oauth``).
"""

from typing import TYPE_CHECKING, Any, Dict

from ....models.api.oauth import GitHubOAuthConfig, GoogleOAuthConfig

if TYPE_CHECKING:
    from ...base.config_model import DjangoConfig

# provider id -> config class; the order is the order buttons are shown in.
PROVIDER_CONFIGS = {"github": GitHubOAuthConfig, "google": GoogleOAuthConfig}


class OAuthSettingsGenerator:
    """Generates the ``GITHUB_OAUTH_CONFIG`` / ``GOOGLE_OAUTH_CONFIG`` settings."""

    def __init__(self, config: "DjangoConfig"):
        self.config = config

    def generate(self) -> Dict[str, Any]:
        settings: Dict[str, Any] = {}
        for provider_id, config_cls in PROVIDER_CONFIGS.items():
            # An explicit object wins, even a half-filled one (a system check reports it).
            provider_config = getattr(self.config, f"{provider_id}_oauth", None) or config_cls.from_env()
            if provider_config is not None:
                settings[f"{provider_id.upper()}_OAUTH_CONFIG"] = provider_config
        return settings


__all__ = ["OAuthSettingsGenerator", "PROVIDER_CONFIGS"]
