"""Optional fallback for servers not behind Cloudflare: a local GeoLite2 or DB-IP Lite `.mmdb` file.

Needs `pip install django-cfg[geoip]` (the `geoip2` package) and `visitor_geo.geoip_path`. MaxMind's GeoLite2 EULA
requires an account, attribution, moving to each new release within 30 days, and no locating of individuals; DB-IP
Lite (CC BY 4.0) needs only attribution. The lookup is local; nothing leaves the server.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import TYPE_CHECKING, Optional

from .countries import continent_of
from .geo import Geo

if TYPE_CHECKING:
    from django_cfg.models.django.visitor_geo import VisitorGeoConfig

logger = logging.getLogger(__name__)


@lru_cache(maxsize=4)
def _reader(path: str):
    try:
        from django.contrib.gis.geoip2 import GeoIP2
    except Exception as exc:  # noqa: BLE001 - geoip2 not installed
        logger.warning("visitor_geo.fallback=geoip2 but geoip2 is unavailable (%s)", exc.__class__.__name__)
        return None
    try:
        return GeoIP2(path)
    except Exception as exc:  # noqa: BLE001 - missing or unreadable database
        logger.warning("visitor_geo: cannot open the GeoIP database at the configured path (%s)", exc.__class__.__name__)
        return None


def lookup(ip: str, config: "VisitorGeoConfig") -> Optional[Geo]:
    if not config.geoip_path:
        return None
    reader = _reader(config.geoip_path)
    if reader is None:
        return None
    try:
        if config.allows("region"):
            data = reader.city(ip)
            geo = Geo(
                country=(data.get("country_code") or "").upper(),
                continent=(data.get("continent_code") or "").upper(),
                region=data.get("region_name") or data.get("region") or "",
                region_code=(data.get("region_code") or "").upper(),
                timezone=data.get("time_zone") or "",
                city=data.get("city") or "",
                postal_code=data.get("postal_code") or "",
                latitude=data.get("latitude"),
                longitude=data.get("longitude"),
                source="geoip2",
            )
        else:
            data = reader.country(ip)
            code = (data.get("country_code") or "").upper()
            geo = Geo(country=code, continent=continent_of(code), source="geoip2")
    except Exception:  # noqa: BLE001 - address not in the database, private address
        return None
    return geo.limited(config) if geo.country else None
