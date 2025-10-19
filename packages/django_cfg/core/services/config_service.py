"""
Configuration service coordinating all builders.

Facade pattern: Provides simple API to DjangoConfig while delegating
to specialized builders for actual work.

Size: ~100 lines (pure coordination, no business logic)
"""

from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from ..base.config_model import DjangoConfig
    from ..builders.apps_builder import InstalledAppsBuilder
    from ..builders.middleware_builder import MiddlewareBuilder
    from ..builders.security_builder import SecurityBuilder


class ConfigService:
    """
    Facade service coordinating all configuration builders.

    This service:
    - Lazy-loads builders on demand
    - Provides simple API for DjangoConfig
    - Coordinates multiple builders

    Example:
        ```python
        service = ConfigService(config)
        apps = service.get_installed_apps()
        middleware = service.get_middleware()
        ```
    """

    def __init__(self, config: "DjangoConfig"):
        """
        Initialize service with configuration.

        Args:
            config: DjangoConfig instance
        """
        self.config = config

        # Lazy initialization of builders
        self._apps_builder: Optional[InstalledAppsBuilder] = None
        self._middleware_builder: Optional[MiddlewareBuilder] = None
        self._security_builder: Optional[SecurityBuilder] = None

    @property
    def apps_builder(self) -> "InstalledAppsBuilder":
        """Lazy-load apps builder."""
        if self._apps_builder is None:
            from ..builders.apps_builder import InstalledAppsBuilder
            self._apps_builder = InstalledAppsBuilder(self.config)
        return self._apps_builder

    @property
    def middleware_builder(self) -> "MiddlewareBuilder":
        """Lazy-load middleware builder."""
        if self._middleware_builder is None:
            from ..builders.middleware_builder import MiddlewareBuilder
            self._middleware_builder = MiddlewareBuilder(self.config)
        return self._middleware_builder

    @property
    def security_builder(self) -> "SecurityBuilder":
        """Lazy-load security builder."""
        if self._security_builder is None:
            from ..builders.security_builder import SecurityBuilder
            self._security_builder = SecurityBuilder(self.config)
        return self._security_builder

    def get_installed_apps(self) -> List[str]:
        """
        Get complete INSTALLED_APPS list.

        Delegates to InstalledAppsBuilder.

        Returns:
            List of Django app labels

        Example:
            >>> service.get_installed_apps()
            ['django.contrib.admin', 'django.contrib.auth', ...]
        """
        return self.apps_builder.build()

    def get_middleware(self) -> List[str]:
        """
        Get complete MIDDLEWARE list.

        Delegates to MiddlewareBuilder.

        Returns:
            List of middleware class paths

        Example:
            >>> service.get_middleware()
            ['django.middleware.security.SecurityMiddleware', ...]
        """
        return self.middleware_builder.build()

    def get_allowed_hosts(self) -> List[str]:
        """
        Get ALLOWED_HOSTS from security configuration.

        Delegates to SecurityBuilder.

        Returns:
            List of allowed host patterns

        Example:
            >>> service.get_allowed_hosts()
            ['localhost', '127.0.0.1', 'example.com']
        """
        return self.security_builder.build_allowed_hosts()


# Export service
__all__ = ["ConfigService"]
