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
    DRAMATIQ = "dramatiq"
    # Future: CELERY = "celery"


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
        default=TaskBackend.DRAMATIQ,
        description="Task processing backend"
    )

    def __init__(self, **data):
        """Initialize TaskConfig with BaseCfgAutoModule support."""
        super().__init__(**data)
        # Initialize _config attribute for BaseCfgAutoModule
        self._config = None

    # === Backend-Specific Configuration ===
    dramatiq: 'DramatiqConfig' = Field(
        default_factory=lambda: None,
        description="Dramatiq-specific configuration"
    )
    worker: 'WorkerConfig' = Field(
        default_factory=lambda: None,
        description="Worker configuration"
    )

    def model_post_init(self, __context: Any) -> None:
        """Initialize backend configs with defaults after model creation."""
        if self.dramatiq is None:
            from .backends import DramatiqConfig
            self.dramatiq = DramatiqConfig()
        if self.worker is None:
            from .backends import WorkerConfig
            self.worker = WorkerConfig()

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

    def get_effective_processes(self, debug: bool = False) -> int:
        """
        Get effective number of processes based on environment.

        Args:
            debug: Whether in debug mode

        Returns:
            Number of worker processes to use

        Example:
            >>> config = TaskConfig()
            >>> config.get_effective_processes(debug=True)
            2
        """
        if debug and self.dev_processes is not None:
            return self.dev_processes
        elif not debug and self.prod_processes is not None:
            return self.prod_processes
        else:
            return self.dramatiq.processes

    def get_effective_queues(self) -> List[str]:
        """
        Get effective queue configuration.

        Returns:
            List of queue names

        Example:
            >>> config = TaskConfig()
            >>> config.get_effective_queues()
            ['default', 'high', 'low']
        """
        return self.dramatiq.queues

    def get_redis_config(self, redis_url: str) -> Dict[str, Any]:
        """
        Generate Redis configuration for Dramatiq.

        Args:
            redis_url: Redis connection URL

        Returns:
            Dictionary with Redis connection parameters

        Example:
            >>> config = TaskConfig()
            >>> config.get_redis_config("redis://localhost:6379/1")
            {'host': 'localhost', 'port': 6379, 'db': 1, 'password': None}
        """
        from urllib.parse import urlparse

        # Parse Redis URL
        parsed = urlparse(redis_url)

        # Build Redis config
        config = {
            "host": parsed.hostname or "localhost",
            "port": parsed.port or 6379,
            "db": self.dramatiq.redis_db,
            "password": parsed.password,
        }

        # Add SSL if specified
        if parsed.scheme == "rediss":
            config["ssl"] = True

        return config

    def get_dramatiq_settings(self, redis_url: str) -> Dict[str, Any]:
        """
        Generate complete Dramatiq settings for Django.

        Args:
            redis_url: Redis connection URL

        Returns:
            Dictionary with complete Dramatiq configuration

        Example:
            >>> config = TaskConfig()
            >>> settings = config.get_dramatiq_settings("redis://localhost:6379/1")
            >>> "DRAMATIQ_BROKER" in settings
            True
        """
        from urllib.parse import urlparse

        redis_config = self.get_redis_config(redis_url)
        parsed = urlparse(redis_url)

        # Build Redis URL with correct database
        redis_url_with_db = redis_url
        if parsed.path and parsed.path != "/":
            # Replace existing database in URL
            redis_url_with_db = redis_url.replace(parsed.path, f"/{self.dramatiq.redis_db}")
        else:
            # Add database to URL
            redis_url_with_db = f"{redis_url.rstrip('/')}/{self.dramatiq.redis_db}"

        return {
            "DRAMATIQ_BROKER": {
                "BROKER": "dramatiq.brokers.redis.RedisBroker",
                "OPTIONS": {
                    "url": redis_url_with_db,
                    **redis_config
                },
            },
            "DRAMATIQ_RESULT_BACKEND": {
                "BACKEND": "dramatiq.results.backends.redis.RedisBackend",
                "BACKEND_OPTIONS": {
                    "url": redis_url_with_db,
                    **redis_config
                },
            },
            "DRAMATIQ_MIDDLEWARE": self.dramatiq.middleware,
            "DRAMATIQ_QUEUES": self.dramatiq.queues,
        }

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
from .backends import DramatiqConfig, WorkerConfig

TaskConfig.model_rebuild()

__all__ = [
    "TaskConfig",
    "TaskBackend",
    "QueuePriority",
    "DramatiqConfig",
    "WorkerConfig",
]
