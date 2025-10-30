"""
Background tasks generator.

Handles ReArq task queue configuration.
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
    - Configure ReArq task queue
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
            Dictionary with ReArq configuration

        Example:
            >>> generator = TasksSettingsGenerator(config)
            >>> settings = generator.generate()
        """
        # Check if tasks should be enabled
        if not self.config.should_enable_tasks():
            logger.debug("⏭️  Tasks disabled")
            return {}

        try:
            return self._generate_rearq_settings()
        except ImportError as e:
            logger.warning(f"Failed to import ReArq: {e}")
            return {}
        except Exception as e:
            logger.error(f"Failed to generate ReArq settings: {e}")
            return {}

    def _generate_rearq_settings(self) -> Dict[str, Any]:
        """
        Generate ReArq-specific settings.

        Returns:
            Dictionary with ReArq configuration
        """
        from django_cfg.models.tasks import TaskConfig

        # Auto-initialize TaskConfig if needed
        task_config = TaskConfig.auto_initialize_if_needed()
        if task_config is None:
            return {}

        # Generate settings via standard method
        settings = task_config.to_django_settings()

        logger.info("✅ ReArq tasks enabled")
        return settings


__all__ = ["TasksSettingsGenerator"]
