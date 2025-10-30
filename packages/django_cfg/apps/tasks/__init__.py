"""
ReArq tasks app for Django-CFG.

Provides async background task processing with Redis queue.
"""

__all__ = [
    "ReArqClient",
    "get_rearq_client",
    "get_tasks_config",
    "get_tasks_config_or_default",
    "task",
    "cron_task",
]


def __getattr__(name):
    """Lazy imports to avoid loading ReArq at Django startup."""
    if name in ("ReArqClient", "get_rearq_client"):
        from .services.client import ReArqClient, get_rearq_client
        return ReArqClient if name == "ReArqClient" else get_rearq_client
    elif name in ("get_tasks_config", "get_tasks_config_or_default"):
        from .services.config_helper import get_tasks_config, get_tasks_config_or_default
        return get_tasks_config if name == "get_tasks_config" else get_tasks_config_or_default
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def task(queue: str = "default", **kwargs):
    """
    Task decorator shortcut.

    Example:
        >>> from django_cfg.apps.tasks import task
        >>>
        >>> @task(queue="default")
        >>> async def my_task(data: str):
        ...     return f"Processed {data}"
        >>>
        >>> # Execute task
        >>> job = await my_task.delay(data="test")
        >>> result = await job.result(timeout=30)
    """
    from .services.client import get_rearq_client
    client = get_rearq_client()
    return client.task(queue=queue, **kwargs)


def cron_task(cron: str, **kwargs):
    """
    Cron task decorator shortcut.

    Args:
        cron: Cron expression (e.g., "0 * * * *" for hourly)

    Example:
        >>> from django_cfg.apps.tasks import cron_task
        >>>
        >>> @cron_task(cron="0 0 * * *")  # Daily at midnight
        >>> async def daily_cleanup():
        ...     return "Cleanup complete"
    """
    from .services.client import get_rearq_client
    client = get_rearq_client()
    return client.cron_task(cron=cron, **kwargs)
