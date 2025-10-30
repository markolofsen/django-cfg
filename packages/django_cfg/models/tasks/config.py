"""
Main task configuration models.

Contains TaskConfig class (main entry point) and related enums.
Size: ~250 lines (focused on main configuration)
"""

import logging
import os
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from django_cfg.models.base import BaseCfgAutoModule

logger = logging.getLogger(__name__)


class TaskBackend(str, Enum):
    """Supported task backends."""
    REARQ = "rearq"


class QueuePriority(str, Enum):
    """Standard queue priorities."""
    CRITICAL = "critical"
    HIGH = "high"
    DEFAULT = "default"
    LOW = "low"
    BACKGROUND = "background"


class TaskConfig(BaseModel, BaseCfgAutoModule):
    """
    High-level task system configuration.

    Main entry point for configuring background task processing in Django-CFG.
    Provides environment-aware defaults and automatic Redis integration.

    Example:
        ```python
        from django_cfg.models.tasks import TaskConfig

        tasks = TaskConfig(
            enabled=True,
            backend=TaskBackend.DRAMATIQ,
        )
        ```
    """

    # === Core Settings ===
    enabled: bool = Field(
        default=True,
        description="Enable background task processing"
    )
    backend: TaskBackend = Field(
        default=TaskBackend.REARQ,
        description="Task processing backend"
    )

    def __init__(self, **data):
        """Initialize TaskConfig with BaseCfgAutoModule support."""
        super().__init__(**data)
        # Initialize _config attribute for BaseCfgAutoModule
        self._config = None

    # === Backend-Specific Configuration ===
    rearq: 'RearqConfig' = Field(
        default_factory=lambda: None,
        description="ReArq-specific configuration"
    )

    def model_post_init(self, __context: Any) -> None:
        """Initialize backend configs with defaults after model creation."""
        if self.rearq is None:
            from .backends import RearqConfig
            self.rearq = RearqConfig()

    # === Environment-Specific Overrides ===
    dev_processes: Optional[int] = Field(
        default=2,
        description="Number of processes in development environment"
    )
    prod_processes: Optional[int] = Field(
        default=None,
        description="Number of processes in production environment"
    )

    # === Auto-Configuration ===
    auto_discover_tasks: bool = Field(
        default=True,
        description="Automatically discover tasks in Django apps"
    )
    task_modules: List[str] = Field(
        default=["tasks"],
        description="Module names to search for tasks"
    )

    @field_validator("enabled")
    @classmethod
    def validate_enabled_with_environment(cls, v: bool) -> bool:
        """Validate task system can be enabled in current environment."""
        if v:
            # Check if we're in a test environment
            if os.getenv("DJANGO_SETTINGS_MODULE", "").endswith("test"):
                logger.info("Task system disabled in test environment")
                return False

            # Additional environment checks can be added here
            # For example, checking if Redis is available

        return v

    def to_django_settings(self) -> Dict[str, Any]:
        """
        Generate Django settings for task system.

        Returns:
            Dictionary with task configuration for Django settings

        Example:
            >>> config = TaskConfig()
            >>> settings = config.to_django_settings()
            >>> "REARQ_REDIS_URL" in settings
            True
        """
        if not self.enabled:
            return {}

        if self.backend == TaskBackend.REARQ:
            return self.rearq.to_django_settings()

        return {}

    def get_smart_defaults(self):
        """
        Get smart default configuration for this module.

        Returns:
            TaskConfig with smart defaults based on environment
        """
        from .utils import get_default_task_config

        config = self.get_config()
        debug = getattr(config, 'debug', False) if config else False
        return get_default_task_config(debug=debug)

    def get_module_config(self):
        """
        Get the final configuration for this module.

        Returns:
            Self (TaskConfig instance)
        """
        return self

    @classmethod
    def auto_initialize_if_needed(cls) -> Optional['TaskConfig']:
        """
        Auto-initialize TaskConfig if needed based on config flags.

        Returns:
            TaskConfig instance if should be initialized, None otherwise

        Example:
            >>> task_config = TaskConfig.auto_initialize_if_needed()
            >>> if task_config:
            ...     print("Tasks enabled")
        """
        # Get config through BaseCfgModule
        from django_cfg.modules import BaseCfgModule
        base_module = BaseCfgModule()
        config = base_module.get_config()

        if not config:
            return None

        # Check if TaskConfig already exists
        if hasattr(config, 'tasks') and config.tasks is not None:
            # Set config reference and return existing
            config.tasks.set_config(config)
            return config.tasks

        # Check if tasks should be enabled
        if config.should_enable_tasks():
            # Auto-initialize with smart defaults
            task_config = cls().get_smart_defaults()
            task_config.set_config(config)
            config.tasks = task_config

            logger.info("🚀 Auto-initialized TaskConfig (enabled by knowbase/agents/tasks flags)")

            return task_config

        return None


# Resolve forward references for Pydantic v2
from .backends import RearqConfig

TaskConfig.model_rebuild()

__all__ = [
    "TaskConfig",
    "TaskBackend",
    "QueuePriority",
    "RearqConfig",
]
