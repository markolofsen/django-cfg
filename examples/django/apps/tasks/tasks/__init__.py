"""
Tasks package for Django CFG Tasks app.

This package contains Dramatiq actors for background task processing.
"""

# Import all task modules to ensure actors are registered
from . import demo_tasks

__all__ = ['demo_tasks']
