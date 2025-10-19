"""
UnfoldPydanticAdmin - PydanticAdmin with Unfold support.
"""

from .pydantic_admin import PydanticAdminMixin


def _get_unfold_admin_class():
    """Get Unfold's ModelAdmin as base class."""
    try:
        from unfold.admin import ModelAdmin
        return ModelAdmin
    except ImportError:
        # Fallback to Django's ModelAdmin if Unfold is not installed
        from django.contrib.admin import ModelAdmin
        return ModelAdmin


# Create UnfoldPydanticAdmin dynamically
class UnfoldPydanticAdmin(PydanticAdminMixin, _get_unfold_admin_class()):
    """
    Pydantic-driven admin with Unfold UI support.

    Combines PydanticAdminMixin with Unfold ModelAdmin (or Django ModelAdmin as fallback).
    """
    pass
