"""
Base Module for Django CFG

Provides base functionality for all auto-configuring modules.
"""

from typing import Any, Optional, TYPE_CHECKING
from abc import ABC
import importlib
import os

if TYPE_CHECKING:
    from django_cfg.core.config import DjangoConfig


class BaseCfgModule(ABC):
    """
    Base class for all django_cfg modules.
    
    Provides common functionality and configuration access.
    Auto-discovers configuration from Django settings.
    """
    
    _config_instance: Optional["DjangoConfig"] = None
    
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

    def is_support_enabled(self) -> bool:
        """
        Check if django-cfg Support is enabled.
        
        Returns:
            True if Support is enabled, False otherwise
        """
        return self._get_config_key('enable_support', True)
    
    def is_accounts_enabled(self) -> bool:
        """
        Check if django-cfg Accounts is enabled.
        
        Returns:
            True if Accounts is enabled, False otherwise
        """
        return self._get_config_key('enable_accounts', False)
    
    def is_newsletter_enabled(self) -> bool:
        """
        Check if django-cfg Newsletter is enabled.
        
        Returns:
            True if Newsletter is enabled, False otherwise
        """
        return self._get_config_key('enable_newsletter', False)
    
    def is_leads_enabled(self) -> bool:
        """
        Check if django-cfg Leads is enabled.
        
        Returns:
            True if Leads is enabled, False otherwise
        """
        return self._get_config_key('enable_leads', False)
    
    def is_agents_enabled(self) -> bool:
        """
        Check if django-cfg Agents is enabled.
        
        Returns:
            True if Agents is enabled, False otherwise
        """
        return self._get_config_key('enable_agents', False)
    
    def is_knowbase_enabled(self) -> bool:
        """
        Check if django-cfg Knowbase is enabled.
        
        Returns:
            True if Knowbase is enabled, False otherwise
        """
        return self._get_config_key('enable_knowbase', False)
    
    def should_enable_tasks(self) -> bool:
        """
        Check if django-cfg Tasks is enabled.
        Auto-enables if knowbase or agents are enabled.
        
        Returns:
            True if Tasks is enabled, False otherwise
        """

        return self.get_config().should_enable_tasks()
    
    def is_maintenance_enabled(self) -> bool:
        """
        Check if django-cfg Maintenance is enabled.
        
        Returns:
            True if Maintenance is enabled, False otherwise
        """
        return self._get_config_key('enable_maintenance', False)

    def is_payments_enabled(self) -> bool:
        """
        Check if django-cfg Payments is enabled.
        
        Returns:
            True if Payments is enabled, False otherwise
        """
        payments_config = self._get_config_key('payments', None)
        
        # Only handle PaymentsConfig model
        if payments_config and hasattr(payments_config, 'enabled'):
            return payments_config.enabled
        
        return False


# Export the base class
__all__ = [
    "BaseCfgModule",
]
