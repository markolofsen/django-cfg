"""
DRF Spectacular postprocessing hooks for django-cfg.

Auto-fixes for OpenAPI schema generation.
"""

from .enum_naming import auto_fix_enum_names

__all__ = ['auto_fix_enum_names']
