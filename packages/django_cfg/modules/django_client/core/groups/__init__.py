"""
Application Grouping Module.

Smart grouping of Django apps into separate OpenAPI schemas.
"""

from .manager import GroupManager
from .detector import GroupDetector

__all__ = [
    "GroupManager",
    "GroupDetector",
]
