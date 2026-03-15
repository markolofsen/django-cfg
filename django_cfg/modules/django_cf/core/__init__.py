"""
django_cf.core — reusable foundation for all D1-backed modules.

Any module that needs D1 access (django_monitor, future modules) imports from here:

    from django_cfg.modules.django_cf.core import BaseD1Service, CloudflareD1Client, D1QueryResult
    from django_cfg.modules.django_cf.core import D1Q, D1Column, D1Index, D1Table
"""

from .client import CloudflareD1Client
from .d1_query import D1Column, D1Index, D1Q, D1Table
from .service import BaseD1Service
from .types import D1QueryResult

__all__ = [
    "CloudflareD1Client",
    "BaseD1Service",
    "D1QueryResult",
    "D1Q",
    "D1Column",
    "D1Index",
    "D1Table",
]
