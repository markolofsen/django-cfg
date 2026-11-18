"""
Helper functions for accessing Django-RQ configuration from django-cfg.

Provides utilities to get RQ config and check if RQ is enabled.
"""
import logging

from typing import Optional


logger = logging.getLogger(__name__)


def get_rq_config() -> Optional["DjangoRQConfig"]:
    """
    Get Django-RQ configuration from django-cfg.

    Returns:
        DjangoRQConfig instance or None if not configured

    Example:
        >>> config = get_rq_config()
        >>> if config and config.enabled:
        >>>     print(config.queues)
    """
    try:
        from django_cfg.core.config import get_current_config
        from django_cfg.models.django.django_rq import DjangoRQConfig

        config = get_current_config()
        if not config:
            return None

        django_rq = getattr(config, 'django_rq', None)

        # Type validation
        if django_rq and isinstance(django_rq, DjangoRQConfig):
            return django_rq

        return None

    except Exception as e:
        logger.debug(f"Failed to get RQ config: {e}")
        return None


def is_rq_enabled() -> bool:
    """
    Check if Django-RQ is enabled in django-cfg.

    Returns:
        True if RQ is enabled, False otherwise

    Example:
        >>> if is_rq_enabled():
        >>>     from django_rq import enqueue
        >>>     enqueue(my_task)
    """
    config = get_rq_config()
    if not config:
        return False

    return getattr(config, 'enabled', False)


def get_queue_names() -> list:
    """
    Get list of configured queue names.

    Returns:
        List of queue names from config

    Example:
        >>> queues = get_queue_names()
        >>> print(queues)  # ['default', 'high', 'low']
    """
    config = get_rq_config()
    if not config:
        return []

    queues = getattr(config, 'queues', {})
    if isinstance(queues, dict):
        return list(queues.keys())

    return []


def is_prometheus_enabled() -> bool:
    """
    Check if Prometheus metrics export is enabled.

    Returns:
        True if Prometheus is enabled, False otherwise
    """
    config = get_rq_config()
    if not config:
        return False

    return getattr(config, 'prometheus_enabled', True)


def get_redis_url() -> Optional[str]:
    """
    Get Redis URL with correct database number for RQ isolation.

    Uses DjangoRQConfig.redis_db to ensure proper project isolation.
    The base redis_url from DjangoConfig is combined with redis_db
    from DjangoRQConfig to create the final URL.

    Returns:
        Redis URL string with correct DB (e.g., "redis://localhost:6379/1") or None

    Example:
        >>> redis_url = get_redis_url()
        >>> print(redis_url)  # redis://localhost:6379/1 (if redis_db=1)
    """
    try:
        from django_cfg.core.config import get_current_config

        config = get_current_config()
        if not config:
            return None

        base_redis_url = getattr(config, 'redis_url', None)
        if not base_redis_url:
            return None

        # Get RQ config and use its redis_db for isolation
        rq_config = getattr(config, 'django_rq', None)
        if rq_config and hasattr(rq_config, 'get_redis_url_with_db'):
            return rq_config.get_redis_url_with_db(base_redis_url)

        # Fallback to base URL if no RQ config
        return base_redis_url

    except Exception as e:
        logger.debug(f"Failed to get redis_url: {e}")
        return None
