"""
Base Module for Django CFG

Provides base functionality for all auto-configuring modules.
"""

import importlib
import logging
import os
import traceback
from abc import ABC
from typing import TYPE_CHECKING, Any, List, Optional

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from django_cfg.core.config import DjangoConfig
    from django_cfg.extensions.scanner import DiscoveredExtension


class BaseCfgModule(ABC):
    """
    Base class for all django_cfg modules.

    Provides common functionality and configuration access.
    Auto-discovers configuration from Django settings.
    Includes extension discovery methods via ExtensionMixin pattern.
    """

    _config_instance: Optional["DjangoConfig"] = None
    _extension_cache: Optional[List["DiscoveredExtension"]] = None

    def __init__(self):
        """Initialize the base module."""
        self._config = None

    @classmethod
    def get_config(cls) -> Optional["DjangoConfig"]:
        """Get the DjangoConfig instance automatically."""
        if cls._config_instance is None:
            try:
                cls._config_instance = cls._discover_config()
            except Exception:
                # Return None if config discovery fails (e.g., during Django startup)
                return None
        return cls._config_instance

    @classmethod
    def _discover_config(cls) -> "DjangoConfig":
        """Discover the DjangoConfig instance from Django settings."""
        try:
            # Try to get config from Django settings module
            settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")
            if settings_module:
                settings_mod = importlib.import_module(settings_module)
                if hasattr(settings_mod, "config"):
                    return settings_mod.config

            # Fallback: try to create minimal config from Django settings
            from django.conf import settings

            from django_cfg.core.config import DjangoConfig

            return DjangoConfig(
                project_name=getattr(settings, "PROJECT_NAME", "Django Project"),
                secret_key=settings.SECRET_KEY,
                debug=settings.DEBUG,
                allowed_hosts=settings.ALLOWED_HOSTS,
            )

        except Exception as e:
            raise RuntimeError(f"Could not discover DjangoConfig instance: {e}")

    @classmethod
    def reset_config(cls):
        """Reset the cached config instance (useful for testing)."""
        cls._config_instance = None

    def set_config(self, config: Any) -> None:
        """
        Set the configuration instance.
        
        Args:
            config: The DjangoConfig instance
        """
        self._config = config

    def _get_config_key(self, key: str, default: Any) -> Any:
        """
        Get a key from the configuration instance.
        
        Args:
            key: The key to get
            default: The default value to return if the key is not found
        """
        try:
            # Get config using class method
            config = self.get_config()

            # If config is available, get the key
            if config is not None:
                result = getattr(config, key, default)
                return result

            # Fallback to default if no config available
            return default

        except Exception:
            # Return default on any error
            return default

    # === Extension Discovery Methods ===

    @classmethod
    def _get_discovered_extensions(cls) -> List["DiscoveredExtension"]:
        """
        Get all discovered extensions (cached).

        Returns:
            List of DiscoveredExtension objects
        """
        if cls._extension_cache is not None:
            return cls._extension_cache

        try:
            from django_cfg.extensions import get_extension_loader

            config = cls.get_config()
            if not config or not hasattr(config, "base_dir"):
                logger.warning("_get_discovered_extensions: config or base_dir not available")
                return []

            loader = get_extension_loader(base_path=config.base_dir)
            cls._extension_cache = loader.scanner.discover_all()
            logger.debug(f"_get_discovered_extensions: found {len(cls._extension_cache)} extensions")
            return cls._extension_cache

        except Exception as e:
            logger.error(
                f"_get_discovered_extensions failed: {e}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            return []

    def is_extension_enabled(self, name: str) -> bool:
        """
        Check if an extension is enabled (discovered).

        Args:
            name: Extension name to check

        Returns:
            True if extension is discovered, False otherwise

        Example:
            if self.is_extension_enabled("leads"):
                # leads extension is available
        """
        extensions = self._get_discovered_extensions()
        return any(ext.name == name and ext.is_valid for ext in extensions)

    # === Extension check properties (auto-discovered from extensions/apps/) ===
    is_support_enabled = property(lambda self: self.is_extension_enabled("support"))
    is_newsletter_enabled = property(lambda self: self.is_extension_enabled("newsletter"))
    is_leads_enabled = property(lambda self: self.is_extension_enabled("leads"))
    is_agents_enabled = property(lambda self: self.is_extension_enabled("agents"))
    is_knowbase_enabled = property(lambda self: self.is_extension_enabled("knowbase"))
    is_payments_enabled = property(lambda self: self.is_extension_enabled("payments"))
    is_maintenance_enabled = property(lambda self: self.is_extension_enabled("maintenance"))
    is_backup_enabled = property(lambda self: self.is_extension_enabled("backup"))

    def should_enable_rq(self) -> bool:
        """
        Check if django-cfg RQ is enabled.
        
        Returns:
            True if RQ is enabled, False otherwise
        """
        return self.get_config().should_enable_rq()

    def is_centrifugo_enabled(self) -> bool:
        """
        Check if django-cfg Centrifugo is enabled.

        Returns:
            True if Centrifugo is enabled, False otherwise
        """
        centrifugo_config = self._get_config_key('centrifugo', None)

        # Check if centrifugo config exists and is enabled
        if centrifugo_config and hasattr(centrifugo_config, 'enabled'):
            return centrifugo_config.enabled

        return False

    def is_grpc_enabled(self) -> bool:
        """
        Check if django-cfg gRPC is enabled.

        Returns:
            True if gRPC is enabled, False otherwise
        """
        grpc_config = self._get_config_key('grpc', None)

        # Check if grpc config exists and is enabled
        if grpc_config and hasattr(grpc_config, 'enabled'):
            return grpc_config.enabled

        return False

    def is_webpush_enabled(self) -> bool:
        """
        Check if django-cfg Web Push is enabled.

        Returns:
            True if Web Push is enabled, False otherwise
        """
        webpush_config = self._get_config_key('webpush', None)

        # Check if webpush config exists and is enabled
        if webpush_config and hasattr(webpush_config, 'enabled'):
            return webpush_config.enabled

        return False

    def is_currency_enabled(self) -> bool:
        """
        Check if django-cfg Currency is enabled.

        Returns:
            True if Currency is enabled, False otherwise
        """
        currency_config = self._get_config_key('currency', None)

        # Check if currency config exists and is enabled
        if currency_config and hasattr(currency_config, 'enabled'):
            return currency_config.enabled

        return False

    def is_geo_enabled(self) -> bool:
        """
        Check if django-cfg Geo is enabled.

        Returns:
            True if Geo is enabled, False otherwise
        """
        geo_config = self._get_config_key('geo', None)

        # Check if geo config exists and is enabled
        if geo_config and hasattr(geo_config, 'enabled'):
            return geo_config.enabled

        return False

    def is_totp_enabled(self) -> bool:
        """
        Check if django-cfg TOTP/2FA is enabled.

        Returns:
            True if 2FA is enabled, False otherwise
        """
        two_factor_config = self._get_config_key('two_factor', None)

        # Check if two_factor config exists and is enabled
        if two_factor_config and hasattr(two_factor_config, 'enabled'):
            return two_factor_config.enabled

        # Default: enabled (TOTP app is always available)
        return True

    def is_github_oauth_enabled(self) -> bool:
        """
        Check if GitHub OAuth is enabled and configured.

        Returns:
            True if GitHub OAuth is properly configured, False otherwise
        """
        github_oauth_config = self._get_config_key('github_oauth', None)

        # Check if github_oauth config exists and is properly configured
        if github_oauth_config and hasattr(github_oauth_config, 'is_configured'):
            return github_oauth_config.is_configured()

        return False


# Export the base class
__all__ = [
    "BaseCfgModule",
]
