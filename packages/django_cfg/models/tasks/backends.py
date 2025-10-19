"""
Backend-specific configurations.

Contains Dramatiq and Worker configuration models.
Size: ~200 lines (focused on backend settings)
"""

import logging
import os
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


class DramatiqConfig(BaseModel):
    """
    Dramatiq-specific configuration with production-ready defaults.

    This model provides comprehensive configuration for Dramatiq background
    task processing, including Redis settings, worker configuration,
    middleware stack, and monitoring options.

    Example:
        ```python
        from django_cfg.models.tasks import DramatiqConfig

        dramatiq = DramatiqConfig(
            redis_db=1,
            processes=4,
            threads=8,
        )
        ```
    """

    # === Redis Configuration ===
    redis_db: int = Field(
        default=1,
        ge=0,
        le=15,
        description="Redis database number for tasks (separate from cache)"
    )
    redis_key_prefix: str = Field(
        default="dramatiq",
        description="Redis key prefix for task data"
    )

    # === Task Configuration ===
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Default maximum retry count for failed tasks"
    )
    default_priority: int = Field(
        default=5,
        ge=0,
        le=10,
        description="Default task priority (0=highest, 10=lowest)"
    )
    max_age_seconds: int = Field(
        default=3600,
        ge=60,
        description="Maximum age for tasks before they expire"
    )
    time_limit_seconds: int = Field(
        default=600,
        ge=30,
        description="Maximum execution time per task"
    )

    # === Worker Configuration ===
    processes: int = Field(
        default=4,
        ge=1,
        le=32,
        description="Number of worker processes"
    )
    threads: int = Field(
        default=8,
        ge=1,
        le=64,
        description="Number of threads per worker process"
    )
    queues: List[str] = Field(
        default=["default", "high", "low"],
        description="Available task queues"
    )

    # === Middleware Stack ===
    middleware: List[str] = Field(
        default=[
            "dramatiq.middleware.AgeLimit",
            "dramatiq.middleware.TimeLimit",
            "dramatiq.middleware.Callbacks",
            "dramatiq.middleware.Retries",
            "dramatiq.middleware.Prometheus",
            "django_dramatiq.middleware.AdminMiddleware",
            "django_dramatiq.middleware.DbConnectionsMiddleware",
        ],
        description="Middleware stack for task processing"
    )

    # === Monitoring & Admin ===
    prometheus_enabled: bool = Field(
        default=True,
        description="Enable Prometheus metrics collection"
    )
    admin_enabled: bool = Field(
        default=True,
        description="Enable Django admin interface integration"
    )

    # === Performance Tuning ===
    prefetch_multiplier: int = Field(
        default=2,
        ge=1,
        le=10,
        description="Message prefetch multiplier for workers"
    )
    max_memory_mb: Optional[int] = Field(
        default=512,
        ge=128,
        description="Maximum memory usage per worker (MB)"
    )

    @field_validator("processes")
    @classmethod
    def validate_processes(cls, v: int) -> int:
        """Ensure reasonable process count based on CPU cores."""
        cpu_count = os.cpu_count() or 4
        max_recommended = cpu_count * 2

        if v > max_recommended:
            logger.warning(
                f"Process count ({v}) exceeds recommended maximum ({max_recommended}). "
                f"Consider reducing to avoid resource contention."
            )

        return v

    @field_validator("queues")
    @classmethod
    def validate_queues(cls, v: List[str]) -> List[str]:
        """Ensure queue names are valid and include default."""
        if not v:
            raise ValueError("At least one queue must be specified")

        # Ensure 'default' queue exists
        if "default" not in v:
            v.append("default")

        # Validate queue names (alphanumeric + underscore/hyphen)
        import re
        pattern = re.compile(r'^[a-zA-Z0-9_-]+$')

        for queue in v:
            if not pattern.match(queue):
                raise ValueError(f"Invalid queue name: {queue}. Use only alphanumeric, underscore, and hyphen.")

        return v

    @field_validator("middleware")
    @classmethod
    def validate_middleware(cls, v: List[str]) -> List[str]:
        """Ensure essential middleware is included."""
        essential_middleware = [
            "dramatiq.middleware.Retries",
            "django_dramatiq.middleware.DbConnectionsMiddleware",
        ]

        for middleware in essential_middleware:
            if middleware not in v:
                logger.warning(f"Adding essential middleware: {middleware}")
                v.append(middleware)

        return v


class WorkerConfig(BaseModel):
    """
    Worker process and resource configuration.

    Provides fine-grained control over worker behavior, resource limits,
    and health monitoring settings.

    Example:
        ```python
        from django_cfg.models.tasks import WorkerConfig

        worker = WorkerConfig(
            shutdown_timeout=30,
            max_memory_mb=512,
            health_check_enabled=True,
        )
        ```
    """

    # === Process Management ===
    shutdown_timeout: int = Field(
        default=30,
        ge=5,
        le=300,
        description="Graceful shutdown timeout in seconds"
    )
    heartbeat_interval: int = Field(
        default=5,
        ge=1,
        le=60,
        description="Worker heartbeat interval in seconds"
    )

    # === Resource Limits ===
    max_memory_mb: Optional[int] = Field(
        default=512,
        ge=128,
        description="Maximum memory per worker process (MB)"
    )
    max_cpu_percent: Optional[float] = Field(
        default=80.0,
        ge=10.0,
        le=100.0,
        description="Maximum CPU usage per worker (%)"
    )

    # === Health Monitoring ===
    health_check_enabled: bool = Field(
        default=True,
        description="Enable worker health monitoring"
    )
    restart_on_memory_limit: bool = Field(
        default=True,
        description="Restart worker if memory limit exceeded"
    )

    # === Logging ===
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Worker log level"
    )
    log_format: str = Field(
        default="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        description="Log message format"
    )


__all__ = [
    "DramatiqConfig",
    "WorkerConfig",
]
