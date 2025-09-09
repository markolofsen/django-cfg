"""
Base Module for Django CFG

Provides base functionality for all auto-configuring modules.
"""

from typing import Any, Optional
from abc import ABC


class BaseModule(ABC):
    """
    Base class for all django_cfg modules.
    
    Provides common functionality and configuration access.
    """
    
    def __init__(self):
        """Initialize the base module."""
        self._config = None
    
    def get_config(self) -> Optional[Any]:
        """
        Get the current Django configuration instance.
        
        Returns:
            The current DjangoConfig instance or None
        """
        if self._config is None:
            try:
                # Try to get config from the current context
                from django_cfg.core.config import get_current_config
                self._config = get_current_config()
            except (ImportError, AttributeError):
                # Fallback - config might not be available yet
                pass
        
        return self._config
    
    def set_config(self, config: Any) -> None:
        """
        Set the configuration instance.
        
        Args:
            config: The DjangoConfig instance
        """
        self._config = config
    
    def _get_config_key(self, key: str, default: Any) -> bool:
        """
        Get a key from the configuration instance.
        
        Args:
            key: The key to get
            default: The default value to return if the key is not found
        """
        try:
            # Try to get config if not already set
            if self._config is None:
                self._config = self.get_config()
            
            # If config is available, get the key
            if self._config is not None:
                result = getattr(self._config, key, default)
                return bool(result)
            
            # Fallback to default if no config available
            return bool(default)
            
        except Exception:
            # Return default on any error
            return bool(default)

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


# Export the base class
__all__ = [
    "BaseModule",
]
