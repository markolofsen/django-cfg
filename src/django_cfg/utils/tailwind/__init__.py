"""
Tailwind CSS Configuration Package

This package contains all Tailwind CSS configuration and build tools
for the Django admin interface with semantic colors.
"""

from .config import get_tailwind_config

__all__ = [
    'get_tailwind_config',
]
