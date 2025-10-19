"""
Security settings generator.

Handles Django security configuration.
Size: ~100 lines (focused on security settings)
"""

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from ...base.config_model import DjangoConfig


class SecuritySettingsGenerator:
    """
    Generates security settings.

    Responsibilities:
    - CORS configuration
    - SSL/HTTPS settings
    - Security headers
    - Production security hardening

    Example:
        ```python
        generator = SecuritySettingsGenerator(config)
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
        Generate security settings.

        Uses SecurityBuilder for comprehensive security configuration
        with Docker awareness and automatic domain normalization.

        Returns:
            Dictionary with security configuration

        Example:
            >>> generator = SecuritySettingsGenerator(config)
            >>> settings = generator.generate()
        """
        from ...builders.security_builder import SecurityBuilder

        # Use SecurityBuilder for all security settings
        builder = SecurityBuilder(self.config)
        settings = builder.build_security_settings()

        # Add base Django settings
        base_settings = self._get_base_settings()
        settings.update(base_settings)

        return settings

    def _get_base_settings(self) -> Dict[str, Any]:
        """
        Get base Django settings (non-security specific).

        Returns:
            Dictionary with base settings
        """
        return {
            'USE_TZ': True,
            'USE_I18N': True,
            'USE_L10N': True,
        }


__all__ = ["SecuritySettingsGenerator"]
