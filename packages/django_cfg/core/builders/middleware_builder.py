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

        # Add connection pool cleanup middleware LAST (if enabled)
        # This ensures connections are returned to pool after ALL other middleware
        if self.config.enable_pool_cleanup:
            middleware.append('django_cfg.middleware.pool_cleanup.ConnectionPoolCleanupMiddleware')

        return middleware

    def _get_feature_middleware(self) -> List[str]:
        """
        Get middleware for enabled django-cfg features.

        Returns:
            List of feature-specific middleware class paths
        """
        middleware = []

        # Accounts middleware (user activity tracking)
        # accounts is always enabled - core django-cfg functionality
        middleware.append("django_cfg.middleware.UserActivityMiddleware")

        # Extension middleware (from extensions/apps/)
        # Extensions define middleware via middleware_classes or get_middleware_classes()
        middleware.extend(self._get_extension_middleware())

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

    def _get_extension_middleware(self) -> List[str]:
        """
        Get middleware from auto-discovered extensions.

        Extensions can define middleware via:
        - middleware_classes field in __cfg__.py
        - Override get_middleware_classes() method

        Returns:
            List of middleware class paths from extensions
        """
        try:
            from django_cfg.extensions import get_extension_loader

            loader = get_extension_loader(base_path=self.config.base_dir)
            return loader.get_middleware()
        except Exception as e:
            # Don't fail if extensions module has issues
            from django_cfg.utils import get_logger
            logger = get_logger(__name__)
            logger.debug(f"Extension middleware discovery skipped: {e}")
            return []


# Export builder
__all__ = ["MiddlewareBuilder"]
