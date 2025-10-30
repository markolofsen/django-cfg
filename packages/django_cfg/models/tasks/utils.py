"""
Task configuration utilities.

Contains utility functions for task configuration:
- Smart queue detection
- Environment-aware defaults
- Configuration validation

Size: ~120 lines (focused on utilities)
"""

import logging
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from .config import TaskConfig

logger = logging.getLogger(__name__)


def get_smart_queues(debug: bool = False) -> List[str]:
    """
    Get smart default queues based on enabled modules.

    Automatically detects which django-cfg modules are enabled and adds
    their corresponding queues to the default queue list.

    Args:
        debug: Whether running in debug mode (affects base queues)

    Returns:
        List of queue names appropriate for enabled modules

    Example:
        >>> queues = get_smart_queues(debug=True)
        >>> "default" in queues
        True
    """
    # Base queues
    if debug:
        base_queues = ["default"]
    else:
        base_queues = ["critical", "high", "default", "low", "background"]

    # Try to detect enabled modules and add their queues
    try:
        from django_cfg.modules.base import BaseCfgModule
        base_module = BaseCfgModule()

        # Check for knowbase module (requires "knowbase" queue)
        if base_module.is_knowbase_enabled():
            if "knowbase" not in base_queues:
                base_queues.append("knowbase")

        # Check for payments module (requires "payments" queue)
        if base_module.is_payments_enabled():
            if "payments" not in base_queues:
                base_queues.append("payments")

        # Check for agents module (may require "agents" queue in future)
        if base_module.is_agents_enabled():
            if "agents" not in base_queues:
                base_queues.append("agents")

        logger.info(f"🎯 Smart queue detection: {base_queues}")

    except Exception as e:
        logger.warning(f"Failed to auto-detect queues, using defaults: {e}")

    return base_queues


def get_default_task_config(debug: bool = False) -> 'TaskConfig':
    """
    Get default task configuration based on environment.

    Creates a TaskConfig with sensible defaults for development or production.

    Args:
        debug: Whether in debug/development mode

    Returns:
        TaskConfig with environment-appropriate defaults

    Example:
        >>> config = get_default_task_config(debug=True)
        >>> config.rearq.max_jobs
        10
    """
    from .backends import RearqConfig
    from .config import TaskConfig

    if debug:
        # Development defaults
        return TaskConfig(
            rearq=RearqConfig(
                redis_url="redis://localhost:6379/0",
                db_url="sqlite://./rearq.db",
                max_jobs=5,
                job_timeout=300,
            )
        )
    else:
        # Production defaults
        return TaskConfig(
            rearq=RearqConfig(
                redis_url="redis://localhost:6379/0",
                db_url="postgresql://localhost/rearq",
                max_jobs=20,
                job_timeout=600,
            )
        )


def validate_task_config(config: 'TaskConfig', redis_url: Optional[str] = None) -> bool:
    """
    Validate task configuration and dependencies.

    Checks if the task configuration is valid and all required dependencies are available.

    Args:
        config: TaskConfig to validate
        redis_url: Optional Redis URL to validate

    Returns:
        True if configuration is valid, False otherwise

    Example:
        >>> config = get_default_task_config()
        >>> validate_task_config(config, "redis://localhost:6379/0")
        True
    """
    if not config.enabled:
        return True

    # Check Redis URL if provided
    if redis_url:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(redis_url)
            if not parsed.scheme.startswith("redis"):
                logger.error(f"Invalid Redis URL scheme: {parsed.scheme}")
                return False
        except Exception as e:
            logger.error(f"Invalid Redis URL: {e}")
            return False

    # Check if ReArq is available
    try:
        import rearq
    except ImportError as e:
        logger.error(f"ReArq dependencies not available: {e}")
        return False

    return True


__all__ = [
    "get_smart_queues",
    "get_default_task_config",
    "validate_task_config",
]
