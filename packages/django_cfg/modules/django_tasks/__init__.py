"""
Django-CFG Task Service Module.

Simplified task service for Dramatiq integration with essential functionality.
"""

from .factory import (
    get_task_health,
    get_task_service,
    initialize_task_system,
    is_task_system_available,
    reset_task_service,
)
from .service import DjangoTasks
from .settings import (
    extend_constance_config_with_tasks,
    generate_dramatiq_settings_from_config,
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
