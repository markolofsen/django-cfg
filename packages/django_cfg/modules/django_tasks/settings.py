"""
Dramatiq settings generation.

Functions to generate Dramatiq settings from DjangoConfig.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def generate_dramatiq_settings_from_config(config=None) -> Optional[Dict[str, Any]]:
    """
    Generate Dramatiq settings from DjangoConfig instance.

    Args:
        config: DjangoConfig instance (optional, will auto-discover if not provided)

    Returns:
        Dict[str, Any]: Dramatiq settings dictionary or None if not enabled
    """
    # If config provided, use it directly
    if config is not None:
        try:
            if not hasattr(config, "tasks") or not config.tasks or not config.tasks.enabled:
                return None

            # Get Redis URL from cache configuration
            redis_url = None
            if config.cache_default and hasattr(config.cache_default, 'redis_url'):
                redis_url = config.cache_default.redis_url
            elif config.cache_default and hasattr(config.cache_default, 'location'):
                redis_url = config.cache_default.location
            else:
                redis_url = "redis://localhost:6379"

            if redis_url:
                dramatiq_settings = config.tasks.get_dramatiq_settings(redis_url)
                logger.debug(f"Generated Dramatiq settings with Redis URL: {redis_url}")
                return dramatiq_settings
            else:
                logger.warning("Tasks enabled but no Redis URL available for Dramatiq")
                return None

        except Exception as e:
            logger.error(f"Failed to generate Dramatiq settings: {e}")
            return None

    # Auto-discover config if not provided
    try:
        from ..base import BaseCfgModule

        base_module = BaseCfgModule()
        config = base_module.get_config()

        if not config or not hasattr(config, 'tasks') or not config.tasks or not config.tasks.enabled:
            return None

        # Get Redis URL from cache config or environment
        redis_url = None
        if hasattr(config, 'cache_default') and config.cache_default:
            redis_url = getattr(config.cache_default, 'redis_url', None)

        if not redis_url:
            # Fallback to environment or default
            import os
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/1')

        # Generate Dramatiq settings
        dramatiq_settings = config.tasks.get_dramatiq_settings(redis_url)

        # Ensure we only use Redis broker (no RabbitMQ)
        if 'DRAMATIQ_BROKER' in dramatiq_settings:
            dramatiq_settings['DRAMATIQ_BROKER']['BROKER'] = 'dramatiq.brokers.redis.RedisBroker'

        logger.info(f"✅ Generated Dramatiq settings with Redis broker and {len(config.tasks.dramatiq.queues)} queues")
        return dramatiq_settings

    except Exception as e:
        logger.error(f"Failed to generate Dramatiq settings: {e}")
        return None


def extend_constance_config_with_tasks():
    """Extend Constance configuration with Dramatiq task fields if tasks are enabled."""
    try:
        from .factory import get_task_service

        service = get_task_service()
        if not service.is_enabled():
            logger.debug("Task system not enabled, skipping Constance extension")
            return []

        fields = service.get_constance_fields()
        logger.info(f"🔧 Extended Constance with {len(fields)} task configuration fields")
        return fields

    except Exception as e:
        logger.error(f"Failed to extend Constance config with tasks: {e}")
        return []


__all__ = [
    "generate_dramatiq_settings_from_config",
    "extend_constance_config_with_tasks",
]
