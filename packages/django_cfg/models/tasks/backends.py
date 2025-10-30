"""
Backend-specific configurations.

Contains ReArq configuration model.
Size: ~100 lines (focused on backend settings)
"""

import logging
from typing import Any, Dict

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


class RearqConfig(BaseModel):
    """
    ReArq-specific configuration with production-ready defaults.

    This model provides comprehensive configuration for ReArq async background
    task processing, including Redis settings, worker configuration,
    and job retry policies.

    Example:
        ```python
        from django_cfg.models.tasks import RearqConfig

        rearq = RearqConfig(
            redis_url="redis://localhost:6379/0",
            db_url="sqlite://./rearq.db",
            max_jobs=10,
            job_timeout=300,
        )
        ```
    """

    # === Core Settings ===
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for task queue"
    )
    db_url: str = Field(
        default="sqlite://./rearq.db",
        description="Database URL for job persistence (Tortoise ORM)"
    )

    # === Worker Settings ===
    max_jobs: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum concurrent jobs per worker"
    )
    job_timeout: int = Field(
        default=300,
        ge=30,
        le=3600,
        description="Default job timeout in seconds"
    )
    job_retry: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Default number of retries for failed jobs"
    )
    job_retry_after: int = Field(
        default=60,
        ge=1,
        description="Delay in seconds before retrying failed job"
    )

    # === Cleanup Settings ===
    keep_job_days: int | None = Field(
        default=7,
        ge=1,
        description="Days to keep job history (None = forever)"
    )

    @field_validator("redis_url")
    @classmethod
    def validate_redis_url(cls, v: str) -> str:
        """Validate Redis URL format."""
        if not v.startswith(("redis://", "rediss://")):
            raise ValueError("Redis URL must start with redis:// or rediss://")
        return v

    @field_validator("db_url")
    @classmethod
    def validate_db_url(cls, v: str) -> str:
        """Validate database URL format."""
        valid_schemes = ("sqlite://", "postgres://", "postgresql://", "mysql://")
        if not v.startswith(valid_schemes):
            raise ValueError(f"Database URL must start with one of: {valid_schemes}")
        return v

    def to_django_settings(self) -> Dict[str, Any]:
        """
        Generate Django settings dictionary.

        Returns:
            Dictionary with ReArq configuration for Django settings

        Example:
            >>> config = RearqConfig()
            >>> settings = config.to_django_settings()
            >>> "REARQ_REDIS_URL" in settings
            True
        """
        return {
            "REARQ_REDIS_URL": self.redis_url,
            "REARQ_DB_URL": self.db_url,
            "REARQ_MAX_JOBS": self.max_jobs,
            "REARQ_JOB_TIMEOUT": self.job_timeout,
            "REARQ_JOB_RETRY": self.job_retry,
            "REARQ_JOB_RETRY_AFTER": self.job_retry_after,
            "REARQ_KEEP_JOB_DAYS": self.keep_job_days,
        }


__all__ = [
    "RearqConfig",
]
