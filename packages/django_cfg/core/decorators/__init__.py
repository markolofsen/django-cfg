"""
Django-CFG Core Decorators.

Reusable decorators for views and API endpoints.
"""
from .cors import (
    cors_allow_all,
    cors_origins,
    cors_exempt,
)

__all__ = [
    "cors_allow_all",
    "cors_origins",
    "cors_exempt",
]
