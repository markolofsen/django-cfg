"""
Utility modules for django_cfg.

This package contains utility functions and classes for:
- Smart defaults based on environment
- Path resolution and project structure detection
- Django settings generation helpers
- Logging utilities
"""

# This file intentionally left minimal to avoid circular imports
# All utility classes are imported through the main __init__.py lazy loading mechanism

# Re-export get_logger for convenience
from django_cfg.modules.django_logging import get_logger

__all__ = ["get_logger"]
