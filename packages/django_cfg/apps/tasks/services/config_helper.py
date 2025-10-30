"""
Task configuration helper.

Provides access to task configuration from global state.
"""
from typing import Optional

from django_cfg.modules.django_logging import get_logger

logger = get_logger("tasks.config")


def get_tasks_config():
    """
    Get tasks configuration from global state.

    Returns:
        TaskConfig instance if found, None otherwise

    Example:
        >>> from django_cfg.apps.tasks.services import get_tasks_config
        >>> config = get_tasks_config()
        >>> if config:
        ...     print(config.rearq.redis_url)
    """
    from django_cfg.core import get_current_config

    config = get_current_config()

    if config and hasattr(config, "tasks") and config.tasks:
        return config.tasks

    return None


def get_tasks_config_or_default():
    """
    Get tasks configuration or return default.

    Returns:
        TaskConfig instance (from global state or default)

    Example:
        >>> from django_cfg.apps.tasks.services import get_tasks_config_or_default
        >>> config = get_tasks_config_or_default()
        >>> print(config.rearq.redis_url)
    """
    config = get_tasks_config()

    if config:
        return config

    # Fallback to default
    from django_cfg.models.tasks import TaskConfig

    logger.warning("Tasks config not found in global state, using default")
    return TaskConfig()


__all__ = [
    "get_tasks_config",
    "get_tasks_config_or_default",
]
