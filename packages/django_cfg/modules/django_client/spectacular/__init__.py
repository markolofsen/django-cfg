"""
DRF Spectacular postprocessing hooks for django-cfg.

Auto-fixes and enhancements for OpenAPI schema generation.
"""

from .enum_naming import auto_fix_enum_names
from .async_detection import mark_async_operations

__all__ = ['auto_fix_enum_names', 'mark_async_operations']
