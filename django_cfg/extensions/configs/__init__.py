"""
Extension configuration base classes.

Provides typed Pydantic configuration classes for extensions.
Users extend these base classes in their extension's config.py.
"""

from .apps import *  # noqa: F401, F403
from .modules import *  # noqa: F401, F403
