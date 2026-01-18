"""
Django-RQ Configuration for django-cfg.

Type-safe configuration for django-rq with automatic Django settings generation
and support for scheduled tasks via rq-scheduler.

Django-RQ is a Redis-based task queue: https://github.com/rq/django-rq

Features:
- Type-safe queue and scheduler configuration
- Redis connection management (standard, Sentinel, SSL)
- Job timeout and TTL configuration
- Built-in Prometheus metrics support
- Exception handler configuration
- Admin interface with monitoring
- RQ Scheduler for cron-like scheduling
- High performance (10,000+ jobs/sec)

Example:
    ```python
    from django_cfg.models.django.django_rq import DjangoRQConfig, RQQueueConfig

    django_rq_config = DjangoRQConfig(
        enabled=True,
        queues=[
            RQQueueConfig(
                queue="default",
                host="localhost",
                port=6379,
                db=0,
                default_timeout=360,
            ),
            RQQueueConfig(
                queue="high",
                host="localhost",
                port=6379,
                db=0,
                default_timeout=180,
            ),
        ],
        show_admin_link=True,
        prometheus_enabled=True,
    )
    ```

Scheduler Support:
    Use rq-scheduler for cron-like scheduled tasks:

    ```bash
    pip install rq-scheduler
    python manage.py rqscheduler
    ```

    ```python
    import django_rq
    scheduler = django_rq.get_scheduler('default')

    # Schedule job for specific time
    from datetime import datetime
    scheduler.enqueue_at(datetime(2025, 12, 31, 23, 59), my_task)

    # Schedule job with interval
    scheduler.schedule(
        scheduled_time=datetime.utcnow(),
        func=my_task,
        interval=60,  # Every 60 seconds
        repeat=None,  # Repeat forever
    )

    # Cron-style scheduling
    scheduler.cron(
        "0 0 * * *",  # Every day at midnight
        func=my_task,
        queue_name='default'
    )
    ```
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class RQQueueConfig(BaseModel):
    """
    Configuration for a single RQ queue.

    Supports standard Redis, Redis Sentinel, and SSL connections.
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    # Queue name
    queue: str = Field(
        ...,
        min_length=1,
        max_length=100,
        pattern=r'^[a-zA-Z0-9_-]+$',
        description="Queue name (alphanumeric, hyphens, underscores)",
    )

    # Redis URL (alternative to host/port/db)
    url: Optional[str] = Field(
        default=None,
        description="Redis URL (redis://localhost:6379/0). If provided, overrides host/port/db.",
    )

    # Standard Redis connection
    host: str = Field(
        default="localhost",
        description="Redis host",
    )

    port: int = Field(
        default=6379,
        ge=1,
        le=65535,
        description="Redis port",
    )

    db: int = Field(
        default=0,
        ge=0,
        le=15,
        description="Redis database number (0-15)",
    )

    username: Optional[str] = Field(
        default=None,
        description="Redis username (Redis 6+)",
    )

    password: Optional[str] = Field(
        default=None,
        description="Redis password",
    )

    # Job defaults
    default_timeout: int = Field(
        default=360,
        ge=1,
        description="Default job timeout in seconds",
    )

    default_result_ttl: int = Field(
        default=86400,  # 24 hours - keep results for a day
        ge=0,
        description="Default result TTL in seconds (0 = no expiry, -1 = never expire)",
    )

    failure_ttl: int = Field(
        default=604800,  # 7 days - keep failed jobs for a week for debugging
        ge=0,
        description="Failed job TTL in seconds (how long to keep failed jobs)",
    )

    # Redis Sentinel support
    sentinels: Optional[List[tuple[str, int]]] = Field(
        default=None,
        description="List of Sentinel (host, port) tuples",
    )

    master_name: Optional[str] = Field(
        default=None,
        description="Redis Sentinel master name",
    )

    socket_timeout: Optional[float] = Field(
        default=None,
        ge=0.1,
        description="Redis socket timeout in seconds",
    )

    # Advanced connection options
    connection_kwargs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional Redis connection arguments (e.g., ssl=True)",
    )

    redis_client_kwargs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional Redis client arguments (e.g., ssl_cert_reqs)",
    )

    sentinel_kwargs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Sentinel-specific connection arguments (username/password for Sentinel auth)",
    )

    def to_django_rq_format(self, redis_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert to Django-RQ queue configuration format.

        Args:
            redis_url: Redis URL from parent DjangoConfig (if available)

        Returns:
            Dictionary for RQ_QUEUES[queue_name] in settings.py
        """
        config: Dict[str, Any] = {}

        # Priority: url field > redis_url from parent > Sentinel > host/port/db
        if self.url:
            config["URL"] = self.url
        elif redis_url:
            # Use redis_url from parent DjangoConfig
            config["URL"] = redis_url
        # Use Sentinel if configured
        elif self.sentinels and self.master_name:
            config["SENTINELS"] = self.sentinels
            config["MASTER_NAME"] = self.master_name
            config["DB"] = self.db

            if self.socket_timeout:
                config["SOCKET_TIMEOUT"] = self.socket_timeout

            if self.connection_kwargs:
                config["CONNECTION_KWARGS"] = self.connection_kwargs

            if self.sentinel_kwargs:
                config["SENTINEL_KWARGS"] = self.sentinel_kwargs

        else:
            # Standard Redis connection
            config["HOST"] = self.host
            config["PORT"] = self.port
            config["DB"] = self.db

            if self.redis_client_kwargs:
                config["REDIS_CLIENT_KWARGS"] = self.redis_client_kwargs

        # Common options
        if self.username:
            config["USERNAME"] = self.username

        if self.password:
            config["PASSWORD"] = self.password

        config["DEFAULT_TIMEOUT"] = self.default_timeout
        config["DEFAULT_RESULT_TTL"] = self.default_result_ttl
        config["DEFAULT_FAILURE_TTL"] = self.failure_ttl

        return config


class DjangoRQConfig(BaseModel):
    """
    Complete Django-RQ configuration container.

    Integrates with django-rq for Redis-based task queuing with high performance.
    Automatically adds django_rq to INSTALLED_APPS when enabled.

    Installation:
        ```bash
        pip install django-rq rq-scheduler
        ```

    Running workers:
        ```bash
        # Start worker for default queue
        python manage.py rqworker default

        # Start worker for multiple queues (priority order)
        python manage.py rqworker high default low

        # Start scheduler for scheduled tasks
        python manage.py rqscheduler
        ```

    Admin interface:
        - Visit /django-rq/ to view queues, workers, and jobs
        - Monitor job execution, failures, and performance
        - Manually requeue or delete jobs
        - View worker statistics

    Prometheus metrics:
        When prometheus_enabled=True, metrics are exposed at /django-rq/metrics/
        - rq_jobs_total{queue, status}
        - rq_job_duration_seconds{queue}
        - rq_workers_total{queue}
        - rq_queue_length{queue}
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    enabled: bool = Field(
        default=True,
        description="Enable Django-RQ (auto-adds django_rq to INSTALLED_APPS)",
    )

    queues: List[RQQueueConfig] = Field(
        default_factory=lambda: [
            RQQueueConfig(queue="default"),
        ],
        description="Queue configurations (at least 'default' required)",
    )

    # Admin interface
    show_admin_link: bool = Field(
        default=True,
        description="Show link to RQ admin in Django admin",
    )

    # Exception handlers
    exception_handlers: List[str] = Field(
        default_factory=list,
        description="List of exception handler function paths (e.g., 'myapp.handlers.log_exception')",
    )

    # API access
    api_token: Optional[str] = Field(
        default=None,
        description="API token for statistics endpoint authentication",
    )

    # Prometheus metrics
    prometheus_enabled: bool = Field(
        default=True,
        description="Enable Prometheus metrics at /django-rq/metrics/",
    )

    # Automatic cleanup configuration
    enable_auto_cleanup: bool = Field(
        default=True,
        description=(
            "Enable automatic cleanup of old finished/failed jobs. "
            "Adds cleanup_old_jobs (daily) and cleanup_orphaned_job_keys (weekly) to schedules."
        ),
    )

    cleanup_max_age_days: int = Field(
        default=7,
        ge=1,
        le=365,
        description="Maximum age in days for jobs to keep before cleanup (default: 7 days)",
    )

    # RQ Scheduler - scheduled jobs configuration
    schedules: List["RQScheduleConfig"] = Field(
        default_factory=list,
        description="Scheduled jobs for rq-scheduler (cron-style, interval, or one-time)",
    )

    @field_validator("queues")
    @classmethod
    def validate_unique_queue_names(cls, queues: List[RQQueueConfig]) -> List[RQQueueConfig]:
        """Validate that all queue names are unique."""
        queue_names = [q.queue for q in queues]
        if len(queue_names) != len(set(queue_names)):
            duplicates = [name for name in queue_names if queue_names.count(name) > 1]
            raise ValueError(
                f"Duplicate queue names found: {set(duplicates)}. "
                "Each queue must have a unique name."
            )

        # Ensure 'default' queue exists
        if 'default' not in queue_names:
            raise ValueError(
                "A queue named 'default' is required. "
                "Add RQQueueConfig(queue='default', ...) to the queues list."
            )

        return queues

    @model_validator(mode="after")
    def validate_rq_dependencies(self) -> "DjangoRQConfig":
        """Cross-field validation and dependency checking."""
        # Check dependencies if enabled
        if self.enabled:
            from django_cfg.apps.integrations.rq._cfg import require_rq_feature

            require_rq_feature()

        return self

    def get_all_schedules(self) -> List["RQScheduleConfig"]:
        """
        Get all schedules including auto-cleanup tasks and demo tasks.

        Automatically adds based on configuration:
        - cleanup_old_jobs (daily) - if enable_auto_cleanup=True
        - cleanup_orphaned_job_keys (weekly) - if enable_auto_cleanup=True
        - demo_scheduler_heartbeat (every minute) - if is_development=True

        Returns:
            Combined list of user schedules + auto-generated schedules
        """
        all_schedules = list(self.schedules)

        # Add auto-cleanup tasks (enabled by default)
        if self.enable_auto_cleanup:
            # Daily cleanup of old jobs
            cleanup_jobs_schedule = RQScheduleConfig(
                func="django_cfg.apps.integrations.rq.tasks.maintenance.cleanup_old_jobs",
                interval=86400,  # Once per day
                queue="default",
                kwargs={
                    "max_age_days": self.cleanup_max_age_days,
                    "dry_run": False,
                },
                description=f"Clean up old RQ jobs older than {self.cleanup_max_age_days} days (daily)",
            )

            # Weekly cleanup of orphaned keys
            cleanup_orphaned_schedule = RQScheduleConfig(
                func="django_cfg.apps.integrations.rq.tasks.maintenance.cleanup_orphaned_job_keys",
                interval=604800,  # Once per week
                queue="default",
                kwargs={"dry_run": False},
                description="Clean up orphaned RQ job keys (weekly)",
            )

            all_schedules.extend([cleanup_jobs_schedule, cleanup_orphaned_schedule])

        # Add demo heartbeat task (development only)
        # Need to import here to avoid circular imports at module level
        try:
            from django_cfg.core.state import get_current_config
            config = get_current_config()

            if config and config.is_development:
                demo_heartbeat_schedule = RQScheduleConfig(
                    func="django_cfg.apps.integrations.rq.tasks.demo_tasks.demo_scheduler_heartbeat",
                    interval=60,  # Every minute
                    queue="default",
                    description="RQ Scheduler Heartbeat (demo - development only)",
                )
                all_schedules.append(demo_heartbeat_schedule)
        except Exception:
            # Config not available yet or import error - skip demo task
            pass

        # Auto-discover schedules from extensions
        try:
            from django_cfg.core.state import get_current_config
            config = get_current_config()

            if config:
                # Collect schedules from all enabled extensions
                extension_schedules = self._collect_extension_schedules(config)
                all_schedules.extend(extension_schedules)

                # Collect schedules from internal modules (currency, etc.)
                module_schedules = self._collect_module_schedules(config)
                all_schedules.extend(module_schedules)
        except Exception:
            # Config not available yet or import error - skip extension schedules
            pass

        return all_schedules

    def _collect_module_schedules(self, config: Any) -> list["RQScheduleConfig"]:
        """
        Collect RQ schedules from internal django-cfg modules.

        Currently supports:
        - CurrencyConfig: currency rate update task

        Args:
            config: Current DjangoConfig instance

        Returns:
            list of RQScheduleConfig from all modules
        """
        schedules: list["RQScheduleConfig"] = []

        # Collect from CurrencyConfig if enabled
        if hasattr(config, 'currency') and config.currency:
            try:
                currency_schedules = config.currency.get_rq_schedules()
                if currency_schedules:
                    schedules.extend(currency_schedules)
            except Exception:
                pass

        return schedules

    def _collect_extension_schedules(self, config: Any) -> list["RQScheduleConfig"]:
        """
        Collect RQ schedules from all enabled extensions.

        Delegates to extensions.schedules.get_extension_schedules().

        Args:
            config: Current DjangoConfig instance (unused, kept for API compatibility)

        Returns:
            list of RQScheduleConfig from all extensions
        """
        try:
            from django_cfg.extensions.schedules import get_extension_schedules
            return get_extension_schedules()
        except Exception:
            return []

    def to_django_settings(self, parent_config: Optional[Any] = None) -> Dict[str, Any]:
        """
        Convert to Django settings dictionary.

        Generates RQ_QUEUES and related configuration for Django-RQ.

        Args:
            parent_config: Optional parent DjangoConfig for accessing redis_url

        Returns:
            Dictionary with RQ_QUEUES, RQ_SHOW_ADMIN_LINK, etc.
        """
        if not self.enabled:
            return {}

        settings: Dict[str, Any] = {}

        # Get redis_url from parent config if available
        redis_url = None
        if parent_config and hasattr(parent_config, 'redis_url'):
            redis_url = parent_config.redis_url

        # Generate RQ_QUEUES configuration from list
        rq_queues = {}
        for queue_config in self.queues:
            rq_queues[queue_config.queue] = queue_config.to_django_rq_format(redis_url=redis_url)

        settings["RQ_QUEUES"] = rq_queues
        settings["RQ_SHOW_ADMIN_LINK"] = self.show_admin_link

        if self.exception_handlers:
            settings["RQ_EXCEPTION_HANDLERS"] = self.exception_handlers

        if self.api_token:
            settings["RQ_API_TOKEN"] = self.api_token

        return settings

    def get_queue_names(self) -> List[str]:
        """Get list of configured queue names."""
        return [q.queue for q in self.queues]

    def get_queue_config(self, queue_name: str) -> Optional[RQQueueConfig]:
        """Get configuration for specific queue."""
        for queue in self.queues:
            if queue.queue == queue_name:
                return queue
        return None

    def add_queue(self, config: RQQueueConfig) -> None:
        """
        Add a new queue configuration.

        Args:
            config: RQQueueConfig instance with queue name set

        Raises:
            ValueError: If queue with this name already exists
        """
        if config.queue in self.get_queue_names():
            raise ValueError(f"Queue '{config.queue}' already exists")
        self.queues.append(config)

    def remove_queue(self, queue_name: str) -> bool:
        """
        Remove a queue configuration.

        Args:
            queue_name: Name of the queue to remove

        Returns:
            True if queue was removed, False if not found
        """
        for i, queue in enumerate(self.queues):
            if queue.queue == queue_name:
                self.queues.pop(i)
                return True
        return False


class RQScheduleConfig(BaseModel):
    """
    Configuration for RQ Scheduler scheduled job.

    RQ Scheduler supports:
    - Cron-style scheduling
    - Interval-based scheduling
    - One-time scheduled jobs
    - Declarative task parameters (limit, verbosity, report_type, days, force)

    Example:
        ```python
        # Cron schedule with declarative parameters
        RQScheduleConfig(
            func="myapp.tasks.update_prices",
            cron="*/5 * * * *",  # Every 5 minutes
            queue="default",
            limit=50,  # Type-safe field, automatically added to kwargs
            verbosity=0,  # Type-safe field, automatically added to kwargs
            description="Update coin prices",
        )

        # Interval schedule with declarative parameters
        RQScheduleConfig(
            func="myapp.tasks.cleanup",
            interval=3600,  # Every hour
            queue="low",
            days=7,  # Type-safe field, automatically added to kwargs
            force=True,  # Type-safe field, automatically added to kwargs
        )

        # Traditional way (still works for custom parameters)
        RQScheduleConfig(
            func="myapp.tasks.my_task",
            interval=60,
            kwargs={"custom_param": "value"},
        )
        ```
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",  # Strict validation - use declared fields only
    )

    func: str = Field(
        ...,
        description="Function path (e.g., 'myapp.tasks.my_task')",
    )

    # Schedule type (one of: cron, interval, or scheduled_time)
    cron: Optional[str] = Field(
        default=None,
        description="Cron expression (e.g., '0 0 * * *' for daily at midnight)",
    )

    interval: Optional[int] = Field(
        default=None,
        ge=1,
        description="Interval in seconds for recurring jobs",
    )

    scheduled_time: Optional[str] = Field(
        default=None,
        description="ISO datetime for one-time scheduled job (e.g., '2025-12-31T23:59:59')",
    )

    # Job configuration
    queue: str = Field(
        default="default",
        description="Queue name to enqueue job",
    )

    timeout: Optional[int] = Field(
        default=None,
        ge=1,
        description="Job timeout in seconds (overrides queue default)",
    )

    result_ttl: Optional[int] = Field(
        default=None,
        ge=0,
        description="Result TTL in seconds (overrides queue default)",
    )

    # Function arguments
    args: List[Any] = Field(
        default_factory=list,
        description="Positional arguments for function",
    )

    kwargs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Keyword arguments for function",
    )

    # Metadata
    job_id: Optional[str] = Field(
        default=None,
        description="Custom job ID (generated if not provided)",
    )

    description: Optional[str] = Field(
        default=None,
        description="Human-readable description of the job",
    )

    repeat: Optional[int] = Field(
        default=None,
        ge=1,
        description="Number of times to repeat (None = repeat forever for interval jobs)",
    )

    # Common task parameters (automatically added to kwargs)
    limit: Optional[int] = Field(
        default=None,
        ge=1,
        description="Limit parameter for task (automatically added to kwargs)",
    )

    verbosity: Optional[int] = Field(
        default=None,
        ge=0,
        le=3,
        description="Verbosity level 0-3 (automatically added to kwargs)",
    )

    report_type: Optional[str] = Field(
        default=None,
        description="Report type parameter (automatically added to kwargs)",
    )

    days: Optional[int] = Field(
        default=None,
        ge=1,
        description="Days parameter for task (automatically added to kwargs)",
    )

    force: Optional[bool] = Field(
        default=None,
        description="Force parameter for task (automatically added to kwargs)",
    )

    ignore_errors: Optional[bool] = Field(
        default=None,
        description="Ignore errors parameter - continue execution even if task fails (automatically added to kwargs)",
    )

    @field_validator("cron", "interval", "scheduled_time")
    @classmethod
    def validate_schedule_type(cls, v, info):
        """Ensure at least one schedule type is provided."""
        # This validator is called for each field, so we check after all fields are set
        return v

    @model_validator(mode="after")
    def validate_one_schedule_type(self):
        """Ensure exactly one schedule type is provided and collect task parameters into kwargs."""
        schedule_types = [
            self.cron is not None,
            self.interval is not None,
            self.scheduled_time is not None,
        ]

        if sum(schedule_types) == 0:
            raise ValueError(
                "At least one schedule type must be provided: cron, interval, or scheduled_time"
            )

        if sum(schedule_types) > 1:
            raise ValueError(
                "Only one schedule type can be provided: cron, interval, or scheduled_time"
            )

        # Collect task parameters into kwargs (declarative syntax support)
        task_params = {}

        # Common task parameters that should go into kwargs
        param_fields = ['limit', 'verbosity', 'report_type', 'days', 'force', 'ignore_errors']

        for field_name in param_fields:
            field_value = getattr(self, field_name, None)
            if field_value is not None:
                task_params[field_name] = field_value

        if task_params:
            # Merge task params with existing kwargs
            # Use object.__setattr__ to avoid recursion with validate_assignment=True
            merged_kwargs = {**self.kwargs, **task_params}
            object.__setattr__(self, 'kwargs', merged_kwargs)

        return self


__all__ = [
    "RQQueueConfig",
    "DjangoRQConfig",
    "RQScheduleConfig",
]
