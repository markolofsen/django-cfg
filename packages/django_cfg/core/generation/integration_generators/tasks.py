"""
Background tasks generator.

Handles Dramatiq task queue configuration.
Size: ~100 lines (focused on task processing)
"""

import logging
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from ...base.config_model import DjangoConfig

logger = logging.getLogger(__name__)


class TasksSettingsGenerator:
    """
    Generates background task processing settings.

    Responsibilities:
    - Configure Dramatiq task queue
    - Auto-detect if tasks should be enabled
    - Set up task configuration

    Example:
        ```python
        generator = TasksSettingsGenerator(config)
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
        Generate task processing settings.

        Returns:
            Dictionary with Dramatiq configuration

        Example:
            >>> generator = TasksSettingsGenerator(config)
            >>> settings = generator.generate()
        """
        # Check if tasks should be enabled
        if not self.config.should_enable_tasks():
            logger.debug("⏭️  Dramatiq disabled (no tasks/knowbase/agents)")
            return {}

        try:
            return self._generate_dramatiq_settings()
        except ImportError as e:
            logger.warning(f"Failed to import django_tasks module: {e}")
            return {}
        except Exception as e:
            logger.error(f"Failed to generate Dramatiq settings: {e}")
            return {}

    def _generate_dramatiq_settings(self) -> Dict[str, Any]:
        """
        Generate Dramatiq-specific settings.

        Returns:
            Dictionary with Dramatiq configuration
        """
        from django_cfg.models.tasks import TaskConfig
        from django_cfg.modules.django_tasks import generate_dramatiq_settings_from_config

        # Auto-initialize TaskConfig if needed
        task_config = TaskConfig.auto_initialize_if_needed()
        if task_config is None:
            return {}

        # Generate Dramatiq settings
        dramatiq_settings = generate_dramatiq_settings_from_config()
        if not dramatiq_settings:
            return {}

        logger.info("✅ Dramatiq enabled (tasks/knowbase/agents required)")

        return dramatiq_settings


__all__ = ["TasksSettingsGenerator"]
