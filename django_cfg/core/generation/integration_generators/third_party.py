"""
Third-party integrations generator.

Handles external service integrations like Telegram, Unfold, Constance.
Size: ~150 lines (focused on third-party services)
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from ...base.config_model import DjangoConfig

logger = logging.getLogger(__name__)


class ThirdPartyIntegrationsGenerator:
    """
    Generates third-party integration settings.

    Responsibilities:
    - Telegram bot configuration
    - Unfold admin theme
    - Constance dynamic settings
    - Track enabled integrations

    Example:
        ```python
        generator = ThirdPartyIntegrationsGenerator(config)
        settings = generator.generate()
        ```
    """

    def __init__(self, config: "DjangoConfig"):
        """
        Initialize generator with configuration.

        Args:
            config: DjangoConfig instance
        """
        self.config = config
        self.integrations: List[str] = []

    def generate(self) -> Dict[str, Any]:
        """
        Generate third-party integration settings.

        Returns:
            Dictionary with integration configurations

        Example:
            >>> generator = ThirdPartyIntegrationsGenerator(config)
            >>> settings = generator.generate()
            >>> "DJANGO_CFG_INTEGRATIONS" in settings
            True
        """
        settings = {}

        # Generate settings for each integration
        settings.update(self._generate_telegram_settings())
        settings.update(self._generate_unfold_settings())
        settings.update(self._generate_constance_settings())
        settings.update(self._generate_centrifugo_settings())

        # Track enabled integrations
        if self.integrations:
            settings["DJANGO_CFG_INTEGRATIONS"] = self.integrations

        return settings

    def _generate_telegram_settings(self) -> Dict[str, Any]:
        """
        Generate Telegram bot settings.

        Returns:
            Dictionary with Telegram configuration
        """
        if not self.config.telegram:
            return {}

        telegram_settings = self.config.telegram.to_config_dict()
        self.integrations.append("telegram")

        return {"TELEGRAM_CONFIG": telegram_settings}

    def _generate_unfold_settings(self) -> Dict[str, Any]:
        """
        Generate Unfold admin theme settings.

        Returns:
            Dictionary with Unfold configuration
        """
        if not self.config.unfold:
            return {}

        unfold_settings = self.config.unfold.to_django_settings()
        self.integrations.append("unfold")

        return unfold_settings

    def _generate_constance_settings(self) -> Dict[str, Any]:
        """
        Generate Constance dynamic settings configuration.

        Returns:
            Dictionary with Constance configuration
        """
        if not hasattr(self.config, "constance") or not self.config.constance:
            return {}

        # Set config reference for app fields detection
        self.config.constance.set_config(self.config)

        constance_settings = self.config.constance.to_django_settings()
        self.integrations.append("constance")

        return constance_settings

    def _generate_centrifugo_settings(self) -> Dict[str, Any]:
        """
        Generate Centrifugo settings.

        Returns:
            Dictionary with Centrifugo configuration
        """
        if not hasattr(self.config, "centrifugo") or not self.config.centrifugo:
            return {}

        centrifugo_settings = self.config.centrifugo.to_django_settings()
        self.integrations.append("centrifugo")

        return centrifugo_settings

    def get_enabled_integrations(self) -> List[str]:
        """
        Get list of enabled integrations.

        Returns:
            List of integration names
        """
        return self.integrations


__all__ = ["ThirdPartyIntegrationsGenerator"]
