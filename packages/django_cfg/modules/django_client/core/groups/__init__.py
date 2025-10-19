"""
Application Grouping Module.

Smart grouping of Django apps into separate OpenAPI schemas.
"""

from .detector import GroupDetector
from .manager import GroupManager

__all__ = [
    "GroupManager",
    "GroupDetector",
]
