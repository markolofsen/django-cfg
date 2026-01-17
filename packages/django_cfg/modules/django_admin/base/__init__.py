"""
Base classes for Django Admin.
"""

from .pydantic_admin import PydanticAdmin, PydanticAdminMixin, get_base_admin_class

__all__ = [
    "PydanticAdmin",
    "PydanticAdminMixin",
    "get_base_admin_class",
]
