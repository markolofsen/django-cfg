"""Visitor geography (`request.geo`) from Cloudflare, behind the edge trust check in `core/edge.py`.

    from django_cfg.modules.django_visitor_geo import get_geo, bump_daily
    get_geo(request).country          # "GE", "" when unknown

Config: `DjangoConfig.visitor_geo` (`models/django/visitor_geo.py`); trust: `DjangoConfig.edge`.
Tests: `from django_cfg.modules.django_visitor_geo.testing import override_geo`.
"""

from .counters import bump_daily
from .geo import EMPTY, Geo, get_geo, resolve_geo

__all__ = ["EMPTY", "Geo", "bump_daily", "get_geo", "resolve_geo"]
