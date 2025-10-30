"""
Task processing configuration models for Django-CFG.

This module provides type-safe Pydantic models for configuring background task
processing with ReArq, including worker management, queue configuration,
and monitoring settings.

Architecture:
    config.py - Main TaskConfig and enums
    backends.py - RearqConfig
    utils.py - Utility functions

Example:
    ```python
    from django_cfg.models.tasks import TaskConfig, RearqConfig

    # Basic configuration
    tasks = TaskConfig(
        enabled=True,
        rearq=RearqConfig(
            redis_url="redis://localhost:6379/0",
            max_jobs=10,
        )
    )

    # Get environment-aware defaults
    from django_cfg.models.tasks import get_default_task_config
    tasks = get_default_task_config(debug=True)
    ```
"""

from .backends import RearqConfig
from .config import QueuePriority, TaskBackend, TaskConfig
from .utils import get_default_task_config, get_smart_queues, validate_task_config

__all__ = [
    # Main configuration
    "TaskConfig",
    "TaskBackend",
    "QueuePriority",

    # Backend configurations
    "RearqConfig",

    # Utility functions
    "get_default_task_config",
    "validate_task_config",
    "get_smart_queues",
]
