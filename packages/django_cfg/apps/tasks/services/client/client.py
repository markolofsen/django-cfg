"""
ReArq client wrapper for Django-CFG.

Provides singleton access to ReArq with django-cfg configuration.
"""
from typing import TYPE_CHECKING, Optional

from django_cfg.modules.django_logging import get_logger

if TYPE_CHECKING:
    from rearq import ReArq

logger = get_logger("tasks.client")


class ReArqClient:
    """
    Django wrapper for ReArq client.

    Provides singleton access to ReArq with django-cfg configuration.

    Features:
    - Async task queue with Redis backend
    - Job persistence with Tortoise ORM
    - Built-in retry logic
    - Cron task support
    - Job result tracking

    Example:
        >>> from django_cfg.apps.tasks import get_rearq_client
        >>>
        >>> client = get_rearq_client()
        >>>
        >>> # Define task
        >>> @client.task(queue="default")
        >>> async def process_data(data_id: str):
        ...     # Process data
        ...     return {"status": "done"}
        >>>
        >>> # Execute task
        >>> job = await process_data.delay(data_id="123")
        >>> result = await job.result(timeout=30)
    """

    def __init__(
        self,
        redis_url: str,
        db_url: str,
        max_jobs: int = 10,
        job_timeout: int = 300,
        job_retry: int = 3,
        job_retry_after: int = 60,
        keep_job_days: int | None = 7,
    ):
        """
        Initialize ReArq client.

        Args:
            redis_url: Redis connection URL for task queue
            db_url: Database URL for job persistence (Tortoise ORM)
            max_jobs: Maximum concurrent jobs per worker
            job_timeout: Default job timeout in seconds
            job_retry: Default number of retries for failed jobs
            job_retry_after: Delay in seconds before retrying failed job
            keep_job_days: Days to keep job history (None = forever)
        """
        self.redis_url = redis_url
        self.db_url = db_url
        self.max_jobs = max_jobs
        self.job_timeout = job_timeout
        self.job_retry = job_retry
        self.job_retry_after = job_retry_after
        self.keep_job_days = keep_job_days

        # Lazy import ReArq to avoid distutils issues at startup
        from rearq import ReArq

        # Create ReArq instance
        self.rearq = ReArq(
            redis_url=redis_url,
            job_retry=job_retry,
            job_retry_after=job_retry_after,
            max_jobs=max_jobs,
            job_timeout=job_timeout,
            keep_job_days=keep_job_days,
        )

        logger.info(f"ReArq client initialized: {redis_url}")

    def task(self, queue: str = "default", **kwargs):
        """
        Task decorator for defining async tasks.

        Args:
            queue: Queue name for the task
            **kwargs: Additional task options

        Returns:
            Task decorator

        Example:
            >>> @client.task(queue="default")
            >>> async def my_task(arg1: str):
            ...     return f"Processed {arg1}"
        """
        return self.rearq.task(queue=queue, **kwargs)

    def cron_task(self, cron: str, **kwargs):
        """
        Cron task decorator for scheduled tasks.

        Args:
            cron: Cron expression (e.g., "0 * * * *" for hourly)
            **kwargs: Additional task options

        Returns:
            Task decorator

        Example:
            >>> @client.cron_task(cron="0 0 * * *")  # Daily at midnight
            >>> async def daily_cleanup():
            ...     return "Cleanup complete"
        """
        return self.rearq.task(cron=cron, **kwargs)

    async def close(self):
        """
        Close client connections.

        Call this when shutting down application to clean up resources.

        Example:
            >>> await client.close()
        """
        await self.rearq.close()
        logger.info("ReArq client closed")

    def get_connection_info(self) -> dict:
        """
        Get connection information.

        Returns:
            Dictionary with connection details

        Example:
            >>> info = client.get_connection_info()
            >>> print(info["redis_url"])
        """
        return {
            "redis_url": self.redis_url,
            "db_url": self.db_url,
            "max_jobs": self.max_jobs,
            "job_timeout": self.job_timeout,
            "job_retry": self.job_retry,
            "job_retry_after": self.job_retry_after,
            "keep_job_days": self.keep_job_days,
        }


# ==================== Singleton Pattern ====================

_rearq_client: Optional[ReArqClient] = None
_rearq_client_lock = None


def get_rearq_client(force_new: bool = False) -> ReArqClient:
    """
    Get global ReArq client instance (singleton).

    Creates client from Django settings on first call.
    Subsequent calls return the same instance (thread-safe).

    Args:
        force_new: Force create new instance (for testing)

    Returns:
        ReArqClient instance

    Example:
        >>> from django_cfg.apps.tasks import get_rearq_client
        >>> client = get_rearq_client()
        >>> @client.task(queue="default")
        >>> async def my_task():
        ...     pass
    """
    global _rearq_client, _rearq_client_lock

    if force_new:
        return _create_client_from_settings()

    if _rearq_client is None:
        # Thread-safe singleton creation
        import threading

        if _rearq_client_lock is None:
            _rearq_client_lock = threading.Lock()

        with _rearq_client_lock:
            if _rearq_client is None:
                _rearq_client = _create_client_from_settings()

    return _rearq_client


def _create_client_from_settings() -> ReArqClient:
    """
    Create ReArq client from django-cfg config.

    Returns:
        ReArqClient instance

    Raises:
        ConfigurationError: If settings not configured
    """
    from ..config_helper import get_tasks_config_or_default

    cfg = get_tasks_config_or_default()
    logger.debug(f"Creating ReArq client from config: {cfg.rearq.redis_url}")

    return ReArqClient(
        redis_url=cfg.rearq.redis_url,
        db_url=cfg.rearq.db_url,
        max_jobs=cfg.rearq.max_jobs,
        job_timeout=cfg.rearq.job_timeout,
        job_retry=cfg.rearq.job_retry,
        job_retry_after=cfg.rearq.job_retry_after,
        keep_job_days=cfg.rearq.keep_job_days,
    )


__all__ = [
    "ReArqClient",
    "get_rearq_client",
]
