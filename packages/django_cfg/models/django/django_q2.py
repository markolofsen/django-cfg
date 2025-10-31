"""
Django-Q2 Configuration for django-cfg.

Type-safe configuration for django-q2 (modern fork of django-q) with automatic
Django settings generation and support for scheduled tasks.

Django-Q2 is the actively maintained fork: https://github.com/django-q2/django-q2

Features:
- Type-safe scheduled task definitions
- Django management command support
- Cron-style and interval-based scheduling
- Redis/database broker configuration
- Queue management
- Task result storage
- Monitoring and logging
- Built-in admin interface
- Python 3.8+ and Django 3.2+ support

Migration from django-crontab to django-q2:
1. Replace django-crontab with django-q2 in requirements
2. Convert CrontabConfig to DjangoQ2Config
3. Cron expressions stay the same
4. Add additional features like intervals, hooks, retries
5. Built-in admin interface for monitoring
6. No need to run 'crontab add' - uses Django's own scheduler

Example:
    ```python
    # Old django-crontab
    crontab_config = CrontabConfig(
        jobs=[
            CrontabJobConfig(
                name="Sync balances",
                minute="0",
                hour="*/1",  # Every hour
                command="sync_account_balances",
            )
        ]
    )

    # New django-q2
    django_q2_config = DjangoQ2Config(
        schedules=[
            DjangoQ2ScheduleConfig(
                name="Sync balances",
                schedule_type="hourly",  # Simpler!
                command="sync_account_balances",
            )
        ]
    )
    ```
"""

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DjangoQ2ScheduleConfig(BaseModel):
    """
    Configuration for a single Django-Q2 scheduled task.

    Supports both cron-style and interval-based scheduling.

    Schedule types:
    - cron: Traditional cron expression (e.g., "0 0 * * *")
    - minutes: Every N minutes (e.g., minutes=15)
    - hourly: Every hour (at minute 0)
    - daily: Every day (at midnight)
    - weekly: Every week (Sunday at midnight)
    - monthly: Every month (1st at midnight)
    - yearly: Every year (Jan 1st at midnight)
    - once: Run once at next scheduled time
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    # Task identification
    name: str = Field(
        ...,
        description="Human-readable task name (unique identifier)",
        min_length=1,
        max_length=100,
    )

    # Schedule type
    schedule_type: Literal["cron", "minutes", "hourly", "daily", "weekly", "monthly", "yearly", "once"] = Field(
        default="cron",
        description="Schedule type: cron, minutes, hourly, daily, weekly, monthly, yearly, once",
    )

    # Cron-style schedule (when schedule_type="cron")
    cron: Optional[str] = Field(
        default=None,
        description="Cron expression (e.g., '0 0 * * *' for daily at midnight)",
        pattern=r"^[\d\*\-\,\/\s]+$",
    )

    # Interval-based schedule (when schedule_type="minutes")
    minutes: Optional[int] = Field(
        default=None,
        ge=1,
        le=525600,  # Max 1 year in minutes
        description="Run every N minutes (when schedule_type='minutes')",
    )

    # Task execution configuration
    func: Optional[str] = Field(
        default=None,
        description="Function path (e.g., 'django.core.management.call_command' or 'myapp.tasks.my_task'). Auto-set when 'command' is provided.",
    )

    # Function arguments
    args: Optional[List[Any]] = Field(
        default=None,
        description="Positional arguments for the function",
    )

    kwargs: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Keyword arguments for the function",
    )

    # Management command support (shortcut)
    command: Optional[str] = Field(
        default=None,
        description="Django management command name (auto-sets func to call_command)",
    )

    command_args: Optional[List[str]] = Field(
        default=None,
        description="Management command arguments",
    )

    command_kwargs: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Management command keyword arguments",
    )

    # Task options
    enabled: bool = Field(
        default=True,
        description="Whether task is enabled",
    )

    queue: Optional[str] = Field(
        default=None,
        description="Queue name (None = default queue)",
    )

    timeout: Optional[int] = Field(
        default=None,
        ge=1,
        le=86400,  # Max 24 hours
        description="Task timeout in seconds",
    )

    repeats: int = Field(
        default=-1,
        description="Number of times to repeat (-1 = infinite)",
    )

    hook: Optional[str] = Field(
        default=None,
        description="Hook function to call after task completion",
    )

    cluster: Optional[str] = Field(
        default=None,
        description="Cluster name (for multi-cluster setups)",
    )

    def model_post_init(self, __context: Any) -> None:
        """Validate and setup configuration after initialization."""
        # Validate that either func or command is provided
        if not self.func and not self.command:
            raise ValueError("Either 'func' or 'command' must be provided")

        # Setup management command
        if self.command:
            self.func = "django.core.management.call_command"
            args = [self.command]
            if self.command_args:
                args.extend(self.command_args)
            self.args = args
            if self.command_kwargs:
                self.kwargs = self.command_kwargs

        # Validate schedule configuration
        if self.schedule_type == "cron" and not self.cron:
            raise ValueError("'cron' must be set when schedule_type is 'cron'")

        if self.schedule_type == "minutes" and not self.minutes:
            raise ValueError("'minutes' must be set when schedule_type is 'minutes'")

    def to_django_q_format(self) -> Dict[str, Any]:
        """
        Convert to Django-Q Schedule format.

        Returns:
            Dictionary for ORM.create() or schedule creation
        """
        from django.utils import timezone
        from datetime import timedelta

        # Map our schedule types to Django-Q2 constants
        type_mapping = {
            "once": "O",
            "minutes": "I",
            "hourly": "H",
            "daily": "D",
            "weekly": "W",
            "monthly": "M",
            "yearly": "Y",
            "cron": "C",
        }

        config = {
            "name": self.name,
            "func": self.func,
            "schedule_type": type_mapping.get(self.schedule_type, self.schedule_type.upper()),
            # Set next_run to NOW + 10 seconds for immediate execution on qcluster start
            "next_run": timezone.now() + timedelta(seconds=10),
        }

        # Convert args list to tuple for Django-Q2 scheduler compatibility
        # Django-Q2 scheduler.py:66-69 expects tuple format, not list
        # If list is provided, scheduler wraps it: (list,) instead of converting list -> tuple
        if self.args:
            config["args"] = tuple(self.args) if isinstance(self.args, list) else self.args

        if self.kwargs:
            config["kwargs"] = self.kwargs

        if self.schedule_type == "cron" and self.cron:
            config["cron"] = self.cron

        if self.schedule_type == "minutes" and self.minutes:
            config["minutes"] = self.minutes

        if self.queue:
            config["queue"] = self.queue

        if self.timeout:
            config["timeout"] = self.timeout

        if self.repeats != -1:
            config["repeats"] = self.repeats

        if self.hook:
            config["hook"] = self.hook

        if self.cluster:
            config["cluster"] = self.cluster

        return config


class DjangoQ2Config(BaseModel):
    """
    Complete Django-Q2 configuration container.

    Integrates with django-q2 (modern fork) for scheduled and async task execution.
    Automatically adds django_q to INSTALLED_APPS when enabled.

    Installation:
        pip install django-q2[redis]

    Example:
        ```python
        # MAGIC: broker_url automatically uses config.redis_url! 🎉
        # Just set redis_url once in your DjangoConfig:
        #   redis_url: Optional[str] = env.redis_url

        django_q2_config = DjangoQ2Config(
            enabled=True,
            # broker_url is auto-detected from config.redis_url!
            schedules=[
                DjangoQ2ScheduleConfig(
                    name="Sync balances every hour",
                    schedule_type="hourly",
                    command="sync_account_balances",
                ),
                DjangoQ2ScheduleConfig(
                    name="Cleanup old data daily",
                    schedule_type="cron",
                    cron="0 2 * * *",  # 2 AM daily
                    command="cleanup_old_data",
                    command_kwargs={"days": 30},
                ),
                DjangoQ2ScheduleConfig(
                    name="Quick check every 5 minutes",
                    schedule_type="minutes",
                    minutes=5,
                    command="health_check",
                ),
            ],
        )
        ```

    Admin interface:
        - Visit /admin/django_q/ to view tasks and schedules
        - Monitor task execution, failures, and performance
        - Manually trigger scheduled tasks
        - View task results and logs
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    enabled: bool = Field(
        default=True,
        description="Enable Django-Q (auto-adds django_q to INSTALLED_APPS)",
    )

    schedules: List[DjangoQ2ScheduleConfig] = Field(
        default_factory=list,
        description="List of scheduled tasks",
    )

    # Django-Q broker configuration
    broker_url: str = Field(
        default="redis://localhost:6379/0",
        description="Broker URL (Redis recommended for production)",
    )

    broker_class: Literal["redis", "orm"] = Field(
        default="redis",
        description="Broker backend class (redis or orm)",
    )

    # Queue configuration
    queue_limit: Optional[int] = Field(
        default=50,
        ge=1,
        description="Maximum tasks in queue before rejecting new ones",
    )

    workers: int = Field(
        default=4,
        ge=1,
        le=32,
        description="Number of worker processes",
    )

    timeout: int = Field(
        default=300,
        ge=1,
        le=86400,  # Max 24 hours
        description="Default task timeout in seconds",
    )

    retry: int = Field(
        default=3600,
        ge=0,
        description="Seconds to wait before retrying failed tasks (0 = no retry)",
    )

    # Task result configuration
    save_limit: int = Field(
        default=250,
        ge=0,
        description="Maximum number of successful tasks to save (0 = unlimited)",
    )

    cached: int = Field(
        default=500,
        ge=0,
        description="Maximum number of tasks to cache (0 = disabled)",
    )

    # Monitoring
    monitor_interval: int = Field(
        default=30,
        ge=1,
        description="Seconds between monitor checks",
    )

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Django-Q log level",
    )

    # Advanced options
    compress: bool = Field(
        default=False,
        description="Compress task data",
    )

    catch_up: bool = Field(
        default=True,
        description="Run missed scheduled tasks immediately",
    )

    sync: bool = Field(
        default=False,
        description="Run tasks synchronously (for testing)",
    )

    def get_enabled_schedules(self) -> List[DjangoQ2ScheduleConfig]:
        """Get list of enabled schedules."""
        return [schedule for schedule in self.schedules if schedule.enabled]

    def to_django_settings(self, parent_config: Optional[Any] = None) -> Dict[str, Any]:
        """
        Convert to Django settings dictionary.

        Generates Q_CLUSTER configuration for Django-Q2.

        Args:
            parent_config: Optional parent DjangoConfig for accessing redis_url

        Note: Schedules are created via Django ORM, not settings.
        Use management command: python manage.py qcluster
        """
        if not self.enabled:
            return {}

        # Auto-detect redis_url from parent config if not explicitly set
        broker_url = self.broker_url
        if broker_url == "redis://localhost:6379/0" and parent_config:
            # Use redis_url from parent config if available
            if hasattr(parent_config, 'redis_url') and parent_config.redis_url:
                broker_url = parent_config.redis_url

        # Map short broker names to full class paths
        broker_class_map = {
            "redis": "django_q.brokers.redis_broker.Redis",
            "orm": "django_q.brokers.orm.ORM",
        }

        cluster_config = {
            # Broker
            "name": "django_cfg_cluster",
            "broker": broker_url,
            "broker_class": broker_class_map.get(self.broker_class, self.broker_class),

            # Queue
            "queue_limit": self.queue_limit,
            "workers": self.workers,
            "timeout": self.timeout,
            "retry": self.retry,

            # Results
            "save_limit": self.save_limit,
            "cached": self.cached,

            # Monitoring
            "monitor": self.monitor_interval,

            # Logging
            "log_level": self.log_level,

            # Advanced
            "compress": self.compress,
            "catch_up": self.catch_up,
            "sync": self.sync,

            # Django integration
            "orm": "default",
        }

        # CRITICAL FIX: Django-Q2 uses 'redis' parameter, NOT 'broker'!
        # The 'broker' parameter is ignored by django-q2.
        # We must set 'redis' parameter to the broker_url string.
        if self.broker_class == "redis":
            # Set redis parameter to broker_url (Django-Q2 accepts redis:// URL string)
            cluster_config["redis"] = broker_url

        settings = {
            "Q_CLUSTER": cluster_config
        }

        return settings

    def get_schedule_by_name(self, name: str) -> Optional[DjangoQ2ScheduleConfig]:
        """Get schedule by name."""
        for schedule in self.schedules:
            if schedule.name == name:
                return schedule
        return None

    def get_schedules_by_command(self, command: str) -> List[DjangoQ2ScheduleConfig]:
        """Get all schedules for a specific command."""
        return [
            schedule for schedule in self.schedules
            if schedule.command == command
        ]


__all__ = [
    "DjangoQ2ScheduleConfig",
    "DjangoQ2Config",
]
