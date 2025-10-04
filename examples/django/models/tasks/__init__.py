"""
Task processing configuration models for Django-CFG.

This module provides type-safe Pydantic models for configuring background task
processing with Dramatiq, including worker management, queue configuration,
and monitoring settings.

Architecture:
    config.py - Main TaskConfig and enums
    backends.py - DramatiqConfig and WorkerConfig
    utils.py - Utility functions

Example:
    ```python
    from django_cfg.models.tasks import TaskConfig, DramatiqConfig

    # Basic configuration
    tasks = TaskConfig(
        enabled=True,
        dramatiq=DramatiqConfig(
            processes=4,
            threads=8,
            queues=["default", "high", "low"],
        )
    )

    # Get environment-aware defaults
    from django_cfg.models.tasks import get_default_task_config
    tasks = get_default_task_config(debug=True)
    ```
"""

from .config import TaskConfig, TaskBackend, QueuePriority
from .backends import DramatiqConfig, WorkerConfig
from .utils import get_default_task_config, validate_task_config, get_smart_queues

__all__ = [
    # Main configuration
    "TaskConfig",
    "TaskBackend",
    "QueuePriority",

    # Backend configurations
    "DramatiqConfig",
    "WorkerConfig",

    # Utility functions
    "get_default_task_config",
    "validate_task_config",
    "get_smart_queues",
]
