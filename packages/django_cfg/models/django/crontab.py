"""
Crontab Configuration for django-cfg.

Type-safe configuration for django-crontab with automatic
Django settings generation and support for management commands.

Features:
- Type-safe crontab job definitions
- Django management command support
- Schedule validation
- Timezone support
- Lock file prevention of concurrent runs
- Command prefix configuration
"""

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CrontabJobConfig(BaseModel):
    """
    Configuration for a single crontab job.

    Supports both management commands and Python callables.
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    # Job identification
    name: str = Field(
        ...,
        description="Human-readable job name (for identification and logging)",
        min_length=1,
        max_length=100,
    )

    # Schedule definition (crontab format)
    minute: str = Field(
        default="*",
        description="Crontab minute (0-59, *, */N, or comma-separated)",
    )

    hour: str = Field(
        default="*",
        description="Crontab hour (0-23, *, */N, or comma-separated)",
    )

    day_of_week: str = Field(
        default="*",
        description="Crontab day of week (0-6, *, */N, or comma-separated)",
    )

    day_of_month: str = Field(
        default="*",
        description="Crontab day of month (1-31, *, */N, or comma-separated)",
    )

    month_of_year: str = Field(
        default="*",
        description="Crontab month (1-12, *, */N, or comma-separated)",
    )

    # Job execution configuration
    job_type: Literal["command", "callable"] = Field(
        default="command",
        description="Job type: 'command' for Django management commands, 'callable' for Python functions",
    )

    # For management commands
    command: Optional[str] = Field(
        default=None,
        description="Django management command name (e.g., 'sync_account_balances')",
    )

    command_args: List[str] = Field(
        default_factory=list,
        description="Command positional arguments",
    )

    command_kwargs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Command keyword arguments (e.g., {'verbosity': 0})",
    )

    # For Python callables
    callable_path: Optional[str] = Field(
        default=None,
        description="Full Python path to callable (e.g., 'myapp.tasks.my_task')",
        pattern=r"^[\w.]+$",
    )

    callable_args: List[Any] = Field(
        default_factory=list,
        description="Callable positional arguments",
    )

    callable_kwargs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Callable keyword arguments",
    )

    # Job options
    enabled: bool = Field(
        default=True,
        description="Whether job is enabled",
    )

    comment: Optional[str] = Field(
        default=None,
        description="Optional comment describing the job",
        max_length=200,
    )

    @field_validator("minute", "hour", "day_of_week", "day_of_month", "month_of_year")
    @classmethod
    def validate_crontab_field(cls, v: str) -> str:
        """Validate crontab field format."""
        if v == "*":
            return v

        # Allow */N (e.g., */15)
        if v.startswith("*/"):
            try:
                int(v[2:])
                return v
            except ValueError:
                raise ValueError(f"Invalid step value in crontab field: {v}")

        # Allow ranges (e.g., 1-5)
        if "-" in v:
            parts = v.split("-")
            if len(parts) != 2:
                raise ValueError(f"Invalid range format in crontab field: {v}")
            try:
                int(parts[0])
                int(parts[1])
                return v
            except ValueError:
                raise ValueError(f"Invalid range values in crontab field: {v}")

        # Allow comma-separated (e.g., 1,3,5)
        if "," in v:
            parts = v.split(",")
            try:
                for part in parts:
                    int(part)
                return v
            except ValueError:
                raise ValueError(f"Invalid comma-separated values in crontab field: {v}")

        # Allow single number
        try:
            int(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid crontab field format: {v}")

    def model_post_init(self, __context: Any) -> None:
        """Validate job configuration after initialization."""
        # Ensure either command or callable_path is set
        if self.job_type == "command" and not self.command:
            raise ValueError("'command' must be set when job_type is 'command'")

        if self.job_type == "callable" and not self.callable_path:
            raise ValueError("'callable_path' must be set when job_type is 'callable'")

    @property
    def schedule(self) -> str:
        """Get crontab schedule string."""
        return f"{self.minute} {self.hour} {self.day_of_month} {self.month_of_year} {self.day_of_week}"

    def to_django_crontab_format(self) -> tuple:
        """
        Convert to django-crontab format.

        Returns:
            Tuple for CRONJOBS list entry
        """
        if self.job_type == "command":
            # Format: (schedule, 'django.core.management.call_command', [command, *args], kwargs)
            return (
                self.schedule,
                'django.core.management.call_command',
                [self.command] + self.command_args,
                self.command_kwargs,
            )
        else:
            # Format: (schedule, callable_path, args, kwargs)
            return (
                self.schedule,
                self.callable_path,
                self.callable_args,
                self.callable_kwargs,
            )


class CrontabConfig(BaseModel):
    """
    Complete Crontab configuration container.

    Integrates with django-crontab for scheduled task execution.
    Automatically adds django_crontab to INSTALLED_APPS when enabled.
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    enabled: bool = Field(
        default=True,
        description="Enable crontab scheduling (auto-adds django_crontab to INSTALLED_APPS)",
    )

    jobs: List[CrontabJobConfig] = Field(
        default_factory=list,
        description="List of scheduled jobs",
    )

    # Django-crontab specific options
    command_prefix: Optional[str] = Field(
        default=None,
        description="Command prefix for all cron jobs (e.g., 'DJANGO_SETTINGS_MODULE=api.settings')",
    )

    command_suffix: Optional[str] = Field(
        default=None,
        description="Command suffix for all cron jobs",
    )

    lock_jobs: bool = Field(
        default=True,
        description="Use lock files to prevent concurrent job execution",
    )

    comment: str = Field(
        default="django-crontab jobs",
        description="Comment added to crontab file",
        max_length=100,
    )

    def get_enabled_jobs(self) -> List[CrontabJobConfig]:
        """Get list of enabled jobs."""
        return [job for job in self.jobs if job.enabled]

    def to_django_settings(self) -> Dict[str, Any]:
        """
        Convert to Django settings dictionary.

        Generates CRONJOBS and related settings for django-crontab.
        """
        if not self.enabled:
            return {}

        settings = {}

        # Build CRONJOBS list
        enabled_jobs = self.get_enabled_jobs()
        if enabled_jobs:
            settings["CRONJOBS"] = [
                job.to_django_crontab_format()
                for job in enabled_jobs
            ]

        # Add command prefix if configured
        if self.command_prefix:
            settings["CRONTAB_COMMAND_PREFIX"] = self.command_prefix

        # Add command suffix if configured
        if self.command_suffix:
            settings["CRONTAB_COMMAND_SUFFIX"] = self.command_suffix

        # Add lock jobs setting
        settings["CRONTAB_LOCK_JOBS"] = self.lock_jobs

        # Add comment
        settings["CRONTAB_COMMENT"] = self.comment

        return settings

    def get_job_by_name(self, name: str) -> Optional[CrontabJobConfig]:
        """Get job by name."""
        for job in self.jobs:
            if job.name == name:
                return job
        return None

    def get_jobs_by_command(self, command: str) -> List[CrontabJobConfig]:
        """Get all jobs for a specific command."""
        return [
            job for job in self.jobs
            if job.job_type == "command" and job.command == command
        ]


__all__ = [
    "CrontabJobConfig",
    "CrontabConfig",
]
