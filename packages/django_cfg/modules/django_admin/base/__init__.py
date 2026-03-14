"""
Base classes for Django Admin.
"""

from .pydantic_admin import PydanticAdmin, PydanticAdminMixin, get_base_admin_class
from django_cfg.modules.django_admin.utils import computed_field

__all__ = [
    "PydanticAdmin",
    "PydanticAdminMixin",
    "get_base_admin_class",
    "computed_field",
]
