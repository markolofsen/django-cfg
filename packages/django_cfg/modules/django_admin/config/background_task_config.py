"""
Background task configuration for async operations.
"""

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class BackgroundTaskConfig(BaseModel):
    """
    Configuration for background task processing.

    Used for async operations like testing imported items,
    bulk processing, or long-running operations.

    Example:
        ```python
        background_config = BackgroundTaskConfig(
            enabled=True,
            task_runner='django_rq',
            batch_size=100,
            timeout=300,
        )
        ```
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )

    enabled: bool = Field(
        True,
        description="Enable background task processing"
    )

    task_runner: Literal['django_rq', 'sync'] = Field(
        'sync',
        description="Task runner to use for background operations (django_rq or sync)"
    )

    batch_size: int = Field(
        100,
        ge=1,
        le=10000,
        description="Number of items to process in each batch"
    )

    timeout: int = Field(
        300,
        ge=1,
        le=3600,
        description="Task timeout in seconds (max 1 hour)"
    )

    retry_on_failure: bool = Field(
        True,
        description="Automatically retry failed tasks"
    )

    max_retries: int = Field(
        3,
        ge=0,
        le=10,
        description="Maximum number of retry attempts"
    )

    priority: Literal['high', 'normal', 'low'] = Field(
        'normal',
        description="Task priority in queue"
    )

    def should_use_background(self) -> bool:
        """Check if background processing should be used."""
        return self.enabled and self.task_runner != 'sync'
