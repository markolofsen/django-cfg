"""
Helper functions for accessing Django-RQ configuration from django-cfg.

Provides utilities to get RQ config and check if RQ is enabled.
"""

from typing import Optional

from django_cfg.utils import get_logger

logger = get_logger("rq.config")


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
    Get Redis URL from django-cfg DjangoConfig.

    This is the global Redis URL that is automatically used for:
    - RQ queues (if queue.url is not set)
    - RQ scheduler
    - Cache backend
    - Session backend

    Returns:
        Redis URL string (e.g., "redis://localhost:6379/0") or None

    Example:
        >>> redis_url = get_redis_url()
        >>> print(redis_url)  # redis://localhost:6379/0
    """
    try:
        from django_cfg.core.config import get_current_config

        config = get_current_config()
        if not config:
            return None

        return getattr(config, 'redis_url', None)

    except Exception as e:
        logger.debug(f"Failed to get redis_url: {e}")
        return None


def _generate_deterministic_job_id(schedule_config) -> str:
    """
    Generate deterministic job ID from schedule configuration.

    This ensures that the same schedule always gets the same ID,
    preventing duplicate jobs on restart.

    Args:
        schedule_config: RQScheduleConfig instance

    Returns:
        Deterministic job ID string

    Example:
        >>> config = RQScheduleConfig(func="myapp.tasks.sync", interval=300)
        >>> job_id = _generate_deterministic_job_id(config)
        >>> # Always returns same ID for same config
    """
    import hashlib
    import json

    # Create a unique identifier from function path and key parameters
    components = [
        schedule_config.func,
        schedule_config.queue or "default",
    ]

    # Add schedule-specific components
    if schedule_config.cron:
        components.append(f"cron:{schedule_config.cron}")
    elif schedule_config.interval:
        components.append(f"interval:{schedule_config.interval}")
    elif schedule_config.scheduled_time:
        components.append(f"time:{schedule_config.scheduled_time}")

    # Add args/kwargs if present (to differentiate same function with different params)
    if schedule_config.args:
        components.append(f"args:{json.dumps(schedule_config.args, sort_keys=True)}")
    if schedule_config.kwargs:
        components.append(f"kwargs:{json.dumps(schedule_config.kwargs, sort_keys=True)}")

    # Generate SHA256 hash
    unique_string = "|".join(str(c) for c in components)
    hash_digest = hashlib.sha256(unique_string.encode()).hexdigest()[:16]

    # Create readable job ID
    func_name = schedule_config.func.split(".")[-1]
    return f"schedule_{func_name}_{hash_digest}"


def _cleanup_old_schedules(scheduler, job_id: str):
    """
    Remove existing schedule with the given job_id before registering new one.

    This prevents duplicate jobs from accumulating on restart.

    Args:
        scheduler: RQ Scheduler instance
        job_id: Job ID to remove

    Example:
        >>> _cleanup_old_schedules(scheduler, "schedule_sync_accounts_abc123")
    """
    try:
        # Cancel existing job if it exists
        scheduler.cancel(job_id)
        logger.debug(f"Removed old schedule: {job_id}")
    except Exception:
        # Job doesn't exist, ignore
        pass


def register_schedules_from_config():
    """
    Register scheduled jobs from django-cfg config in rq-scheduler.

    This function should be called on Django startup (from AppConfig.ready()).
    It reads schedules from config.django_rq.schedules and registers them
    in rq-scheduler.

    Features:
    - Generates deterministic job IDs to prevent duplicates
    - Cleans up old versions of jobs before registering new ones
    - Prevents accumulation of orphaned scheduled jobs

    Example:
        >>> from django_cfg.apps.integrations.rq.services import register_schedules_from_config
        >>> register_schedules_from_config()
    """
    try:
        import django_rq
        from rq_scheduler import Scheduler

        config = get_rq_config()
        if not config or not config.enabled:
            logger.debug("RQ not enabled, skipping schedule registration")
            return

        # Get all schedules including auto-cleanup tasks
        schedules = config.get_all_schedules()
        if not schedules:
            logger.debug("No schedules configured")
            return

        # Get scheduler for default queue
        queue = django_rq.get_queue('default')
        scheduler = Scheduler(queue=queue, connection=queue.connection)

        logger.info(f"Registering {len(schedules)} scheduled jobs from config...")

        for schedule_config in schedules:
            try:
                # Import function
                func_path = schedule_config.func
                module_path, func_name = func_path.rsplit('.', 1)

                try:
                    import importlib
                    module = importlib.import_module(module_path)
                    func = getattr(module, func_name)
                except (ImportError, AttributeError) as e:
                    logger.warning(f"Failed to import function {func_path}: {e}")
                    continue

                # Generate deterministic job ID if not provided
                job_id = schedule_config.job_id
                if not job_id:
                    job_id = _generate_deterministic_job_id(schedule_config)

                # Clean up old version of this schedule
                _cleanup_old_schedules(scheduler, job_id)

                # Get schedule type and register
                if schedule_config.cron:
                    # Suppress FutureWarning from crontab library (rq-scheduler dependency)
                    import warnings
                    with warnings.catch_warnings():
                        warnings.filterwarnings('ignore', category=FutureWarning)
                        scheduler.cron(
                            schedule_config.cron,
                            func=func,
                            args=schedule_config.args,
                            kwargs=schedule_config.kwargs,
                            queue_name=schedule_config.queue,
                            timeout=schedule_config.timeout,
                            result_ttl=schedule_config.result_ttl,
                            id=job_id,
                            repeat=schedule_config.repeat,
                        )
                    logger.info(f"✓ Registered cron schedule: {func_path} ({schedule_config.cron})")

                elif schedule_config.interval:
                    from datetime import datetime
                    scheduler.schedule(
                        scheduled_time=datetime.utcnow(),  # Start immediately
                        func=func,
                        args=schedule_config.args,
                        kwargs=schedule_config.kwargs,
                        interval=schedule_config.interval,
                        queue_name=schedule_config.queue,
                        timeout=schedule_config.timeout,
                        result_ttl=schedule_config.result_ttl,
                        id=job_id,
                        repeat=schedule_config.repeat,
                    )
                    logger.info(f"✓ Registered interval schedule: {func_path} (every {schedule_config.interval}s)")

                elif schedule_config.scheduled_time:
                    from datetime import datetime
                    scheduled_dt = datetime.fromisoformat(schedule_config.scheduled_time)

                    scheduler.schedule(
                        scheduled_time=scheduled_dt,
                        func=func,
                        args=schedule_config.args,
                        kwargs=schedule_config.kwargs,
                        queue_name=schedule_config.queue,
                        timeout=schedule_config.timeout,
                        result_ttl=schedule_config.result_ttl,
                        id=job_id,
                    )
                    logger.info(f"✓ Registered one-time schedule: {func_path} (at {schedule_config.scheduled_time})")

            except Exception as e:
                logger.error(f"Failed to register schedule {schedule_config.func}: {e}")
                continue

        logger.info("Schedule registration completed")

    except Exception as e:
        logger.error(f"Failed to register schedules: {e}", exc_info=True)
