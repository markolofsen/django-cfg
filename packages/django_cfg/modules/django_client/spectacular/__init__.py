"""
DRF Spectacular hooks and schema classes for django-cfg.

Auto-fixes and enhancements for OpenAPI schema generation.
"""

from .async_detection import mark_async_operations
from .enum_naming import auto_fix_enum_names
from .schema import PathBasedAutoSchema

__all__ = ['auto_fix_enum_names', 'mark_async_operations', 'PathBasedAutoSchema']
