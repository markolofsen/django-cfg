"""
API Encryption settings generator.

Note: Encryption settings are accessed directly from DjangoConfig via
get_current_config().encryption, not through Django settings.

This generator exists for consistency with the orchestrator pattern
but returns an empty dict since no Django settings are needed.
"""

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from ...base.config_model import DjangoConfig


class EncryptionSettingsGenerator:
    """
    Placeholder generator for API encryption.

    Encryption configuration is accessed directly from DjangoConfig
    at runtime via get_current_config().encryption.

    No Django settings are generated because:
    - All config is declarative in DjangoConfig
    - Middleware/serializers read from config directly
    - No environment variable overrides needed
    """

    def __init__(self, config: "DjangoConfig"):
        self.config = config

    def generate(self) -> Dict[str, Any]:
        """Return empty dict - encryption reads from config directly."""
        return {}


__all__ = ["EncryptionSettingsGenerator"]
