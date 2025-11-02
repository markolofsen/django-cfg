"""
Demo and test tasks for RQ testing and simulation.

These tasks are used for testing RQ functionality from the frontend.
"""

from .demo_tasks import (
    demo_success_task,
    demo_failure_task,
    demo_slow_task,
    demo_progress_task,
    demo_crash_task,
    demo_retry_task,
)

__all__ = [
    'demo_success_task',
    'demo_failure_task',
    'demo_slow_task',
    'demo_progress_task',
    'demo_crash_task',
    'demo_retry_task',
]
