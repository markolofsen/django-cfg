"""
Cache settings generator.

Handles CACHES configuration and session storage.
Size: ~90 lines (focused on cache settings)
"""

import logging
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from ...base.config_model import DjangoConfig

logger = logging.getLogger(__name__)


class CacheSettingsGenerator:
    """
    Generates Django CACHES settings.

    Responsibilities:
    - Convert CacheConfig models to Django format
    - Provide default cache backend
    - Configure sessions cache
    - Auto-discover additional cache backends

    Example:
        ```python
        generator = CacheSettingsGenerator(config)
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
        Generate cache settings.

        Returns:
            Dictionary with CACHES and session configuration

        Example:
            >>> generator = CacheSettingsGenerator(config)
            >>> settings = generator.generate()
            >>> "CACHES" in settings
            True
        """
        settings = {}
        caches = {}

        # Default cache - always provide one
        if self.config.cache_default:
            # User explicitly configured cache_default
            caches["default"] = self.config.cache_default.to_django_config(
                self.config.env_mode,
                self.config.debug,
                "default"
            )
        elif self.config.redis_url:
            # Auto-create Redis cache from redis_url
            logger.info(f"Auto-creating Redis cache from redis_url: {self.config.redis_url}")
            caches["default"] = self._get_redis_cache_config()
        else:
            # Fallback to default cache backend (LocMem/FileBased depending on env)
            caches["default"] = self._get_default_cache_config()

        # Sessions cache
        if self.config.cache_sessions:
            caches["sessions"] = self.config.cache_sessions.to_django_config(
                self.config.env_mode,
                self.config.debug,
                "sessions"
            )

            # Configure Django to use cache for sessions
            settings["SESSION_ENGINE"] = "django.contrib.sessions.backends.cache"
            settings["SESSION_CACHE_ALIAS"] = "sessions"

        # Auto-discover additional cache backends
        additional_caches = self._discover_additional_caches()
        caches.update(additional_caches)

        if caches:
            settings["CACHES"] = caches

        return settings

    def _get_redis_cache_config(self) -> Dict[str, Any]:
        """
        Auto-create Redis cache from config.redis_url.

        Returns:
            Dictionary with Redis cache backend configuration
        """
        from ....models.infrastructure.cache import CacheConfig

        redis_cache = CacheConfig(
            redis_url=self.config.redis_url,
            timeout=300,  # 5 minutes default
            max_connections=50,
            key_prefix=self.config.project_name.lower().replace(" ", "_") if self.config.project_name else "django",
        )
        return redis_cache.to_django_config(
            self.config.env_mode,
            self.config.debug,
            "default"
        )

    def _get_default_cache_config(self) -> Dict[str, Any]:
        """
        Get default cache configuration (fallback when no redis_url).

        Returns:
            Dictionary with default cache backend configuration
        """
        from ....models.infrastructure.cache import CacheConfig

        default_cache = CacheConfig()
        return default_cache.to_django_config(
            self.config.env_mode,
            self.config.debug,
            "default"
        )

    def _discover_additional_caches(self) -> Dict[str, Dict[str, Any]]:
        """
        Auto-discover additional cache backends.

        Looks for attributes starting with "cache_" (excluding cache_default and cache_sessions).

        Returns:
            Dictionary of additional cache configurations
        """
        additional_caches = {}

        for attr_name in dir(self.config):
            if attr_name.startswith("cache_") and attr_name not in ["cache_default", "cache_sessions"]:
                cache_obj = getattr(self.config, attr_name)
                if hasattr(cache_obj, "to_django_config"):
                    cache_alias = attr_name.replace("cache_", "")
                    additional_caches[cache_alias] = cache_obj.to_django_config(
                        self.config.env_mode,
                        self.config.debug,
                        cache_alias
                    )

        return additional_caches


__all__ = ["CacheSettingsGenerator"]
