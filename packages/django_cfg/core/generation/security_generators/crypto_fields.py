"""
Django Crypto Fields settings generator.

Generates encryption settings for django-crypto-fields with smart defaults.
"""

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from ...base.config_model import DjangoConfig


class CryptoFieldsSettingsGenerator:
    """
    Generates django-crypto-fields encryption settings.

    Responsibilities:
    - DJANGO_CRYPTO_FIELDS_KEY_PATH
    - KEY_PREFIX
    - AUTO_CREATE_KEYS
    - Environment-aware defaults

    Example:
        ```python
        generator = CryptoFieldsSettingsGenerator(config)
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

    def generate(self) -> Dict[str, Any]:
        """
        Generate django-crypto-fields settings.

        Returns:
            Dictionary with encryption settings (empty if disabled)

        Example:
            >>> config = DjangoConfig(project_name="Test", secret_key="x"*50)
            >>> generator = CryptoFieldsSettingsGenerator(config)
            >>> settings = generator.generate()
            >>> isinstance(settings, dict)
            True
        """
        # Only generate settings if crypto_fields is configured
        if not hasattr(self.config, 'crypto_fields') or not self.config.crypto_fields:
            return {}

        crypto_config = self.config.crypto_fields

        # Skip if disabled
        if not crypto_config.enabled:
            return {}

        # Generate settings using config's to_django_settings method
        return crypto_config.to_django_settings(
            base_dir=self.config.base_dir,
            is_production=self.config.is_production,
            debug=self.config.debug,
            project_version=self.config.project_version
        )


__all__ = ["CryptoFieldsSettingsGenerator"]
