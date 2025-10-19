"""
Generator protocols for type safety.

Defines interfaces that all settings generators must implement.
"""

from typing import TYPE_CHECKING, Any, Dict, Protocol

if TYPE_CHECKING:
    from ..base.config_model import DjangoConfig


class SettingsGeneratorProtocol(Protocol):
    """Protocol for all settings generators."""

    def __init__(self, config: "DjangoConfig") -> None:
        """Initialize generator with configuration."""
        ...

    def generate(self) -> Dict[str, Any]:
        """
        Generate Django settings dictionary.

        Returns:
            Dictionary of Django settings
        """
        ...


__all__ = ["SettingsGeneratorProtocol"]
