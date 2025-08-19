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


# Export the base class
__all__ = [
    "BaseModule",
]
