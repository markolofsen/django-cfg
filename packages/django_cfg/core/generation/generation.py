"""
Django settings generation for django_cfg.

Main facade for settings generation.

Following CRITICAL_REQUIREMENTS.md:
- No raw Dict/Any usage
- Proper type annotations
- Comprehensive error handling
- Performance-aware generation
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from ..base.config_model import DjangoConfig

logger = logging.getLogger(__name__)


class SettingsGenerator:
    """
    Generates complete Django settings from DjangoConfig instances.

    Converts type-safe Pydantic configuration models into Django-compatible
    settings dictionaries with intelligent defaults and validation.

    This is a facade class that delegates to SettingsOrchestrator for
    actual generation.

    Example:
        ```python
        from django_cfg import DjangoConfig
        from django_cfg.core.generation import SettingsGenerator

        config = DjangoConfig(project_name="MyProject", secret_key="x"*50)
        settings = SettingsGenerator.generate(config)
        ```
    """

    @classmethod
    def generate(cls, config: "DjangoConfig") -> Dict[str, Any]:
        """
        Generate complete Django settings dictionary.

        Args:
            config: DjangoConfig instance

        Returns:
            Complete Django settings dictionary

        Raises:
            ConfigurationError: If settings generation fails

        Example:
            >>> from django_cfg import DjangoConfig
            >>> config = DjangoConfig(project_name="Test", secret_key="x"*50)
            >>> settings = SettingsGenerator.generate(config)
            >>> "SECRET_KEY" in settings
            True
        """
        from .orchestrator import SettingsOrchestrator

        orchestrator = SettingsOrchestrator(config)
        return orchestrator.generate()

    @classmethod
    def validate_generated_settings(cls, settings: Dict[str, Any]) -> List[str]:
        """
        Validate generated Django settings.

        Args:
            settings: Generated Django settings

        Returns:
            List of validation errors (empty if valid)

        Example:
            >>> settings = {"SECRET_KEY": "x"*50, "DEBUG": True}
            >>> errors = SettingsGenerator.validate_generated_settings(settings)
            >>> if errors:
            ...     print("Validation errors:", errors)
        """
        from .orchestrator import SettingsOrchestrator

        return SettingsOrchestrator.validate_settings(settings)


__all__ = ["SettingsGenerator"]
