"""
Schedule configuration model for extension apps.
"""

from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator


class ExtensionScheduleConfig(BaseModel):
    """
    Declarative schedule configuration for extensions.

    Simplified model for defining RQ schedules in extension settings.
    Converts to RQScheduleConfig when get_rq_schedules() is called.

    Example:
        ```python
        class MyExtSettings(BaseExtensionSettings):
            schedules = [
                ExtensionScheduleConfig(
                    task="cleanup",  # -> extensions.apps.myext.tasks.cleanup
                    cron="0 3 * * *",
                    description="Daily cleanup",
                ),
                ExtensionScheduleConfig(
                    task="sync_data",
                    interval=3600,  # Every hour
                    queue="low",
                ),
            ]
        ```
    """

    # Task name (relative to extension's tasks module)
    # e.g., "cleanup" -> "extensions.apps.{ext_name}.tasks.cleanup"
    task: str = Field(..., description="Task function name (relative to tasks module)")

    # Full function path (overrides task if specified)
    func: Optional[str] = Field(default=None, description="Full function path (overrides task)")

    # Schedule type (one of: cron or interval)
    cron: Optional[str] = Field(default=None, description="Cron expression (e.g., '0 2 * * *')")
    interval: Optional[int] = Field(default=None, ge=1, description="Interval in seconds")

    # Queue
    queue: str = Field(default="default", description="RQ queue name")

    # Optional
    description: Optional[str] = Field(default=None, description="Human-readable description")
    timeout: Optional[int] = Field(default=None, ge=1, description="Job timeout in seconds")

    # Task parameters (passed as kwargs)
    kwargs: dict[str, Any] = Field(default_factory=dict, description="Task keyword arguments")

    @model_validator(mode="after")
    def validate_schedule_type(self) -> "ExtensionScheduleConfig":
        """Ensure exactly one schedule type is provided."""
        if self.cron is None and self.interval is None:
            raise ValueError("Either 'cron' or 'interval' must be specified")
        if self.cron is not None and self.interval is not None:
            raise ValueError("Only one of 'cron' or 'interval' can be specified")
        return self

    def to_rq_schedule(self, extension_name: str) -> Any:
        """
        Convert to RQScheduleConfig.

        Args:
            extension_name: Name of the extension (for building func path)

        Returns:
            RQScheduleConfig instance
        """
        from django_cfg.models.django.django_rq import RQScheduleConfig

        # Build full function path
        if self.func:
            func_path = self.func
        else:
            func_path = f"extensions.apps.{extension_name}.tasks.{self.task}"

        config_kwargs: dict[str, Any] = {
            "func": func_path,
            "queue": self.queue,
        }

        if self.cron:
            config_kwargs["cron"] = self.cron
        if self.interval:
            config_kwargs["interval"] = self.interval
        if self.description:
            config_kwargs["description"] = self.description
        if self.timeout:
            config_kwargs["timeout"] = self.timeout
        if self.kwargs:
            config_kwargs["kwargs"] = self.kwargs

        return RQScheduleConfig(**config_kwargs)
