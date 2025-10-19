"""
MIDDLEWARE builder for Django-CFG.

Single Responsibility: Build Django MIDDLEWARE list from configuration.
Extracted from original config.py for better maintainability.

Size: ~120 lines (focused on middleware logic)
"""

from typing import TYPE_CHECKING, List

from ..constants import DEFAULT_MIDDLEWARE

if TYPE_CHECKING:
    from ..base.config_model import DjangoConfig


class MiddlewareBuilder:
    """
    Builds MIDDLEWARE list from DjangoConfig.

    Responsibilities:
    - Add default Django middleware
    - Insert CORS middleware if security domains configured
    - Add feature-specific middleware (accounts, payments)
    - Add custom user middleware
    - Maintain correct middleware ordering

    Example:
        ```python
        builder = MiddlewareBuilder(config)
        middleware = builder.build()
        ```
    """

    def __init__(self, config: "DjangoConfig"):
        """
        Initialize builder with configuration.

        Args:
            config: DjangoConfig instance
        """
        self.config = config

    def build(self) -> List[str]:
        """
        Build complete MIDDLEWARE list.

        Returns:
            List of middleware class paths in correct order

        Example:
            >>> config = DjangoConfig(security_domains=["example.com"])
            >>> builder = MiddlewareBuilder(config)
            >>> middleware = builder.build()
            >>> "corsheaders.middleware.CorsMiddleware" in middleware
            True
        """
        # Start with default middleware (already includes CorsMiddleware)
        middleware = list(DEFAULT_MIDDLEWARE)

        # Add django-cfg feature-specific middleware
        feature_middleware = self._get_feature_middleware()
        middleware.extend(feature_middleware)

        # Add custom user middleware
        middleware.extend(self.config.custom_middleware)

        return middleware

    def _get_feature_middleware(self) -> List[str]:
        """
        Get middleware for enabled django-cfg features.

        Returns:
            List of feature-specific middleware class paths
        """
        middleware = []

        # Accounts middleware (user activity tracking)
        if self.config.enable_accounts:
            middleware.append("django_cfg.middleware.UserActivityMiddleware")

        # Payments middleware (if enabled and configured)
        if self.config.payments and self.config.payments.enabled:
            payment_middleware = self.config.payments.get_middleware_classes()
            middleware.extend(payment_middleware)

        # Tailwind CSS middleware (browser reload in development)
        # Note: Must be after middleware that encodes responses (like GZipMiddleware)
        if self.config.debug:
            try:
                import django_browser_reload
                middleware.append("django_browser_reload.middleware.BrowserReloadMiddleware")
            except ImportError:
                # django-browser-reload not installed, skip it
                pass

        return middleware


# Export builder
__all__ = ["MiddlewareBuilder"]
