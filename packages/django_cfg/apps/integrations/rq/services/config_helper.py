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

    This function should ONLY be called from the rqscheduler management command,
    NOT from AppConfig.ready() or other places. This prevents race conditions
    when multiple containers start simultaneously.

    Features:
    - Uses distributed lock to prevent race conditions
    - Generates deterministic job IDs to prevent duplicates
    - Cleans up old versions of jobs before registering new ones
    - Prevents accumulation of orphaned scheduled jobs

    Example:
        >>> from django_cfg.apps.integrations.rq.services import register_schedules_from_config
        >>> register_schedules_from_config()
    """
    try:
        import sys
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

        # Determine which queue the rqscheduler daemon is running for
        # by checking --queue argument. This is important because
        # rq-scheduler daemon only processes jobs registered with
        # a Scheduler instance for the SAME queue.
        scheduler_queue = 'default'
        if '--queue' in sys.argv:
            try:
                queue_idx = sys.argv.index('--queue')
                if queue_idx + 1 < len(sys.argv):
                    scheduler_queue = sys.argv[queue_idx + 1]
            except (ValueError, IndexError):
                pass

        # Create Scheduler for the daemon's queue
        # All schedules will be registered here, and queue_name parameter
        # determines where the job gets pushed when it runs
        queue = django_rq.get_queue(scheduler_queue)
        scheduler = Scheduler(queue=queue, connection=queue.connection)
        connection = queue.connection

        logger.info(f"Using scheduler for queue: {scheduler_queue}")

        # Use distributed lock to prevent race conditions
        # Lock expires after 60 seconds in case of crash
        lock_key = "django_cfg:schedule_registration_lock"
        lock_timeout = 60

        # Try to acquire lock using SETNX (atomic operation)
        lock_acquired = connection.set(lock_key, "1", nx=True, ex=lock_timeout)
        if not lock_acquired:
            logger.info("Another process is registering schedules, skipping...")
            return

        try:
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

                    # Target queue for job execution (can differ from scheduler's queue)
                    target_queue = schedule_config.queue or 'default'

                    # Clean up old version of this schedule
                    _cleanup_old_schedules(scheduler, job_id)

                    # Get schedule type and register
                    if schedule_config.cron:
                        # Suppress FutureWarning from crontab library (rq-scheduler dependency)
                        import warnings
                        with warnings.catch_warnings():
                            warnings.filterwarnings('ignore', category=FutureWarning)
                            # For cron schedules, repeat=None means infinite in rq-scheduler
                            cron_kwargs = {
                                "cron_string": schedule_config.cron,
                                "func": func,
                                "args": schedule_config.args,
                                "kwargs": schedule_config.kwargs,
                                "queue_name": target_queue,
                                "timeout": schedule_config.timeout,
                                "result_ttl": schedule_config.result_ttl,
                                "id": job_id,
                            }
                            # Only pass repeat if explicitly set (not None)
                            if schedule_config.repeat is not None:
                                cron_kwargs["repeat"] = schedule_config.repeat

                            scheduler.cron(**cron_kwargs)
                        logger.info(f"✓ Registered cron schedule: {func_path} ({schedule_config.cron}) -> queue={target_queue}")

                    elif schedule_config.interval:
                        from datetime import datetime
                        # For interval schedules, repeat=None means infinite repetition in rq-scheduler
                        # If schedule_config.repeat is set, use it; otherwise omit for infinite
                        schedule_kwargs = {
                            "scheduled_time": datetime.utcnow(),  # Start immediately
                            "func": func,
                            "args": schedule_config.args,
                            "kwargs": schedule_config.kwargs,
                            "interval": schedule_config.interval,
                            "queue_name": target_queue,
                            "timeout": schedule_config.timeout,
                            "result_ttl": schedule_config.result_ttl,
                            "id": job_id,
                        }
                        # IMPORTANT: Always pass repeat parameter explicitly
                        # rq-scheduler defaults to repeat=1 (run once) if not specified
                        # We need repeat=None for infinite repetition
                        schedule_kwargs["repeat"] = schedule_config.repeat  # None = infinite

                        # Debug: log before calling schedule
                        logger.info(f"DEBUG: Calling scheduler.schedule() for {func_path}")
                        logger.info(f"DEBUG: func={func}, func.__module__={getattr(func, '__module__', 'N/A')}, func.__name__={getattr(func, '__name__', 'N/A')}")
                        logger.info(f"DEBUG: schedule_kwargs={schedule_kwargs}")

                        job = scheduler.schedule(**schedule_kwargs)

                        # Debug: log after calling schedule
                        logger.info(f"DEBUG: scheduler.schedule() returned: {job}")
                        if job:
                            logger.info(f"DEBUG: job.id={job.id}, job.func_name={job.func_name}, job.meta={job.meta}")
                            # Verify job is in Redis
                            in_redis = connection.zscore(scheduler.scheduled_jobs_key, job.id)
                            logger.info(f"DEBUG: job in scheduled_jobs: {in_redis is not None}")
                            logger.info(f"✓ Registered interval schedule: {func_path} (every {schedule_config.interval}s) -> queue={target_queue}, job_id={job.id}")
                        else:
                            logger.error(f"✗ scheduler.schedule() returned None for {func_path}")

                    elif schedule_config.scheduled_time:
                        from datetime import datetime
                        scheduled_dt = datetime.fromisoformat(schedule_config.scheduled_time)

                        scheduler.schedule(
                            scheduled_time=scheduled_dt,
                            func=func,
                            args=schedule_config.args,
                            kwargs=schedule_config.kwargs,
                            queue_name=target_queue,
                            timeout=schedule_config.timeout,
                            result_ttl=schedule_config.result_ttl,
                            id=job_id,
                        )
                        logger.info(f"✓ Registered one-time schedule: {func_path} (at {schedule_config.scheduled_time}) -> queue={target_queue}")

                except Exception as e:
                    import traceback
                    logger.error(f"Failed to register schedule {schedule_config.func}: {e}\n{traceback.format_exc()}")
                    continue

            logger.info("Schedule registration completed")

        finally:
            # Always release the lock
            connection.delete(lock_key)
            logger.debug("Released schedule registration lock")

    except Exception as e:
        logger.error(f"Failed to register schedules: {e}", exc_info=True)
