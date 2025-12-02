"""
OAuth settings generator.

Handles OAuth provider configuration for Django settings.
"""

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from ...base.config_model import DjangoConfig


class OAuthSettingsGenerator:
    """
    Generates OAuth settings.

    Responsibilities:
    - GITHUB_OAUTH_CONFIG for GitHub OAuth
    - Future: GOOGLE_OAUTH_CONFIG, etc.

    Example:
        ```python
        generator = OAuthSettingsGenerator(config)
        settings = generator.generate()
        # Returns: {'GITHUB_OAUTH_CONFIG': GitHubOAuthConfig(...)}
        ```
    """

    def __init__(self, config: "DjangoConfig"):
        """
        Initialize generator with configuration.

        Args:
            config: DjangoConfig instance
        """
        self.config = config

    def generate(self) -> Dict[str, Any]:
        """
        Generate OAuth settings.

        Returns:
            Dictionary with OAuth configuration objects

        Example:
            >>> generator = OAuthSettingsGenerator(config)
            >>> settings = generator.generate()
            >>> 'GITHUB_OAUTH_CONFIG' in settings
            True
        """
        settings: Dict[str, Any] = {}

        # GitHub OAuth
        if self.config.github_oauth:
            settings['GITHUB_OAUTH_CONFIG'] = self.config.github_oauth

        # Future providers can be added here:
        # if self.config.google_oauth:
        #     settings['GOOGLE_OAUTH_CONFIG'] = self.config.google_oauth

        return settings


__all__ = ["OAuthSettingsGenerator"]
