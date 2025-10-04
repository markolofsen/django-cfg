"""
Base Configuration Module for Django CFG

Provides a unified base class for all auto-configuration modules.
"""

from typing import Optional, TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from django_cfg.core.config import DjangoConfig


class BaseCfgAutoModule(ABC):
    """
    Base class for all django-cfg auto-configuration modules.
    
    Provides unified configuration access and smart defaults.
    Designed to be used in generation.py without circular imports.
    """
    
    def __init__(self, config: Optional["DjangoConfig"] = None):
        """
        Initialize the auto-configuration module.
        
        Args:
            config: DjangoConfig instance (passed from generation.py)
        """
        self._config = config
    
    def set_config(self, config: "DjangoConfig") -> None:
        """
        Set the configuration instance.
        
        Args:
            config: The DjangoConfig instance
        """
        self._config = config
    
    def get_config(self) -> Optional["DjangoConfig"]:
        """Get the current configuration instance."""
        return self._config
    
    def has_config_field(self, field_name: str) -> bool:
        """
        Check if config has a specific field with a non-None value.
        
        Args:
            field_name: Name of the field to check
            
        Returns:
            True if field exists and is not None
        """
        if not self._config:
            return False
        return hasattr(self._config, field_name) and getattr(self._config, field_name) is not None
    
    def get_config_field(self, field_name: str, default=None):
        """
        Get a field value from config with fallback.
        
        Args:
            field_name: Name of the field to get
            default: Default value if field doesn't exist or is None
            
        Returns:
            Field value or default
        """
        if not self._config:
            return default
        return getattr(self._config, field_name, default)
    
    @abstractmethod
    def get_smart_defaults(self):
        """
        Get smart default configuration for this module.
        
        Returns:
            Configuration object with intelligent defaults
        """
        pass
    
    @abstractmethod
    def get_module_config(self):
        """
        Get the final configuration for this module.
        
        Uses project config if available, otherwise returns smart defaults.
        
        Returns:
            Configuration object ready for Django settings generation
        """
        pass


# Export the base class
__all__ = [
    "BaseCfgAutoModule",
]
