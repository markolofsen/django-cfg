"""
Django-CFG Task Service Module.

Simplified task service for Dramatiq integration with essential functionality.
"""

from .service import DjangoTasks
from .factory import (
    get_task_service,
    reset_task_service,
    is_task_system_available,
    get_task_health,
    initialize_task_system,
)
from .settings import (
    generate_dramatiq_settings_from_config,
    extend_constance_config_with_tasks,
)

__all__ = [
    "DjangoTasks",
    "get_task_service",
    "reset_task_service",
    "is_task_system_available",
    "get_task_health",
    "generate_dramatiq_settings_from_config",
    "extend_constance_config_with_tasks",
    "initialize_task_system",
]
