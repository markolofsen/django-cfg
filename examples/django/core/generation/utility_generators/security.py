"""
Security settings generator.

Handles Django security configuration.
Size: ~100 lines (focused on security settings)
"""

from typing import Dict, Any, TYPE_CHECKING

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

        Returns:
            Dictionary with security configuration

        Example:
            >>> generator = SecuritySettingsGenerator(config)
            >>> settings = generator.generate()
        """
        settings = {}

        # Generate security defaults if domains or SSL redirect are configured
        if self.config.security_domains or self.config.ssl_redirect is not None:
            security_defaults = self._get_security_defaults()
            settings.update(security_defaults)

        # Additional security settings for production
        if self.config.env_mode == "production":
            production_security = self._get_production_security()
            settings.update(production_security)

        return settings

    def _get_security_defaults(self) -> Dict[str, Any]:
        """
        Get security defaults based on configuration.

        Returns:
            Dictionary with security defaults
        """
        from ....utils.smart_defaults import SmartDefaults

        security_defaults = SmartDefaults.get_security_defaults(
            self.config.security_domains,
            self.config.env_mode,
            self.config.debug,
            self.config.ssl_redirect,
            self.config.cors_allow_headers
        )

        return security_defaults

    def _get_production_security(self) -> Dict[str, Any]:
        """
        Get production-specific security settings.

        Returns:
            Dictionary with production security settings
        """
        return {
            "SECURE_SSL_REDIRECT": True,
            "SECURE_HSTS_SECONDS": 31536000,  # 1 year
            "SECURE_HSTS_INCLUDE_SUBDOMAINS": True,
            "SECURE_HSTS_PRELOAD": True,
            "SESSION_COOKIE_SECURE": True,
            "CSRF_COOKIE_SECURE": True,
        }


__all__ = ["SecuritySettingsGenerator"]
