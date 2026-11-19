"""`Geo`: where the visitor is, as far as config allows. Never holds an IP address.

Sources, in order: a test override (`override_geo`), Cloudflare headers when `core/edge.py` trusts the request, the
optional geoip2 database, `visitor_geo.dev_override` while DEBUG. Every field has an empty default; nothing is `None`
except the numbers that have no neutral value (coordinates, ASN, bot score).
"""

from __future__ import annotations

import contextvars
from dataclasses import asdict, dataclass, fields, replace
from typing import TYPE_CHECKING, Any, Dict, Optional
from urllib.parse import unquote

from .countries import EU, continent_of, country_name

if TYPE_CHECKING:
    from django_cfg.core.edge import Edge
    from django_cfg.models.django.visitor_geo import VisitorGeoConfig

# Set by `override_geo` (testing.py); wins over everything, in tests and in code that renders "as if from X".
_override: contextvars.ContextVar[Optional["Geo"]] = contextvars.ContextVar("cfg_geo_override", default=None)

_REGION_FIELDS = ("region", "region_code", "timezone")
_CITY_FIELDS = ("city", "postal_code", "metro_code", "latitude", "longitude")


@dataclass(frozen=True, slots=True)
class Geo:
    country: str = ""          # ISO 3166-1 alpha-2, upper case; "" when unknown, XX or Tor
    is_tor: bool = False
    continent: str = ""        # AF AN AS EU NA OC SA
    colo: str = ""             # Cloudflare data centre (cf-ray suffix)
    region: str = ""
    region_code: str = ""
    timezone: str = ""
    city: str = ""
    postal_code: str = ""
    metro_code: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    asn: Optional[int] = None
    bot_score: Optional[int] = None
    verified_bot: bool = False
    source: str = "none"       # cloudflare | geoip2 | override | dev | none
    trusted: bool = False      # the edge vouched for the request (core/edge.py)

    @property
    def is_eu(self) -> bool:
        return self.country in EU

    @property
    def country_name(self) -> str:
        return country_name(self.country)

    def __bool__(self) -> bool:
        return bool(self.country)

    def __str__(self) -> str:
        """`Tbilisi, Georgia`, `Georgia`, or "" — for emails and admin."""
        name = self.country_name or self.country
        return ", ".join(part for part in (self.city, name) if part)

    def as_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["is_eu"] = self.is_eu
        data["country_name"] = self.country_name
        return data

    def bucket(self, level: str = "country") -> tuple:
        """Key to count by: (country,), (country, region_code) or (country, region_code, city)."""
        if level == "city":
            return (self.country, self.region_code, self.city)
        if level == "region":
            return (self.country, self.region_code)
        return (self.country,)

    def country_record(self):
        """The geo reference app's `Country` row, when that app is installed and has it; otherwise None."""
        if not self.country:
            return None
        from django.apps import apps

        if not apps.is_installed("django_cfg.apps.tools.geo"):
            return None
        try:
            from django_cfg.apps.tools.geo.models import Country

            return Country.objects.filter(iso2=self.country).first()
        except Exception:  # noqa: BLE001 - a missing table must not break a page
            return None

    def limited(self, config: "VisitorGeoConfig") -> "Geo":
        """Drop what config does not allow and round coordinates."""
        if config.level == "off":
            return EMPTY
        changes: Dict[str, Any] = {}
        if not config.allows("region"):
            changes.update({name: "" for name in _REGION_FIELDS})
        if not config.allows("city"):
            changes.update({name: ("" if name not in ("latitude", "longitude") else None) for name in _CITY_FIELDS})
        else:
            for name in ("latitude", "longitude"):
                value = getattr(self, name)
                if value is not None:
                    changes[name] = round(value, config.coords_precision)
        if not config.asn:
            changes["asn"] = None
        if not config.bot:
            changes.update(bot_score=None, verified_bot=False)
        return replace(self, **changes) if changes else self


EMPTY = Geo()
FIELD_NAMES = tuple(f.name for f in fields(Geo))


# ── parsing ─────────────────────────────────────────────────────────────────────────────────────────────────────────


def _text(meta, name: str, limit: int = 120) -> str:
    raw = (meta.get(name) or "").strip()
    if not raw:
        return ""
    if "%" in raw:  # Cloudflare documents "converted to UTF-8"; accept a percent-encoded value too
        raw = unquote(raw)
    try:  # WSGI hands headers over as latin-1; recover UTF-8 bytes sent raw
        raw = raw.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    return "".join(ch for ch in raw if ch.isprintable())[:limit]


def _float(meta, name: str, lo: float, hi: float) -> Optional[float]:
    try:
        value = float((meta.get(name) or "").strip())
    except ValueError:
        return None
    return value if lo <= value <= hi else None


def _int(meta, name: str, lo: int, hi: int) -> Optional[int]:
    text = (meta.get(name) or "").strip().upper().removeprefix("AS")
    if not text.isdigit():
        return None
    value = int(text)
    return value if lo <= value <= hi else None


def _meta_key(header: str) -> str:
    return "HTTP_" + header.upper().replace("-", "_")


def from_cloudflare(meta, config: "VisitorGeoConfig") -> Geo:
    """Parse Cloudflare's headers. The caller has already established that the edge is trusted."""
    raw_country = (meta.get("HTTP_CF_IPCOUNTRY") or "").strip().upper()
    is_tor = raw_country == "T1"
    country = raw_country if len(raw_country) == 2 and raw_country.isalpha() and raw_country not in ("XX", "T1") else ""
    continent = (meta.get("HTTP_CF_IPCONTINENT") or "").strip().upper()[:2] or continent_of(country)
    ray = (meta.get("HTTP_CF_RAY") or "").strip()
    colo = ray.rsplit("-", 1)[1].upper()[:4] if "-" in ray else ""
    verified = (meta.get("HTTP_CF_VERIFIED_BOT") or "").strip().lower() == "true"
    geo = Geo(
        country=country,
        is_tor=is_tor,
        continent=continent if country or continent else "",
        colo=colo if colo.isalpha() else "",
        region=_text(meta, "HTTP_CF_REGION"),
        region_code=_text(meta, "HTTP_CF_REGION_CODE", 10).upper(),
        timezone=_text(meta, "HTTP_CF_TIMEZONE", 64),
        city=_text(meta, "HTTP_CF_IPCITY"),
        postal_code=_text(meta, "HTTP_CF_POSTAL_CODE", 16),
        metro_code=_text(meta, "HTTP_CF_METRO_CODE", 8),
        latitude=_float(meta, "HTTP_CF_IPLATITUDE", -90, 90),
        longitude=_float(meta, "HTTP_CF_IPLONGITUDE", -180, 180),
        asn=_int(meta, _meta_key(config.asn_header), 1, 4_294_967_295),
        bot_score=_int(meta, "HTTP_CF_BOT_SCORE", 1, 99),
        verified_bot=verified,
        source="cloudflare",
        trusted=True,
    )
    return geo.limited(config)


def _from_override(value, source: str, trusted: bool, config: "VisitorGeoConfig") -> Geo:
    data = value.model_dump() if hasattr(value, "model_dump") else dict(value)
    country = (data.pop("country", "") or "").upper()
    data = {k: v for k, v in data.items() if k in FIELD_NAMES}
    geo = Geo(country=country, continent=continent_of(country), source=source, trusted=trusted, **data)
    return geo.limited(config)


def resolve_geo(request, edge: Optional["Edge"] = None, config: Optional["VisitorGeoConfig"] = None) -> Geo:
    """Geography for a request. Pure apart from reading settings; the middleware caches it lazily."""
    from django_cfg.core.edge import get_edge

    config = config or get_visitor_geo_config()
    forced = _override.get()
    if forced is not None:
        return forced.limited(config)
    if config.level == "off":
        return EMPTY
    edge = edge or get_edge(request)
    if edge.trusted and request.META.get("HTTP_CF_IPCOUNTRY") is not None:
        return from_cloudflare(request.META, config)
    if config.fallback == "geoip2" and edge.client_ip:
        from .geoip import lookup

        found = lookup(edge.client_ip, config)
        if found is not None:
            return found
    if config.dev_override is not None and not edge.trusted:
        from django.conf import settings

        if settings.DEBUG:
            return _from_override(config.dev_override, "dev", False, config)
    return EMPTY


def get_visitor_geo_config() -> "VisitorGeoConfig":
    from django_cfg.core.state.registry import get_current_config

    current = get_current_config()
    value = getattr(current, "visitor_geo", None) if current is not None else None
    if value is None:
        from django_cfg.models.django.visitor_geo import VisitorGeoConfig

        value = VisitorGeoConfig()
    return value


def get_geo(request) -> Geo:
    """`request.geo` when the middleware ran, otherwise resolved on the spot (RequestFactory, DRF wrappers)."""
    inner = getattr(request, "_request", None)
    if inner is not None:
        request = inner
    geo = getattr(request, "geo", None)
    if isinstance(geo, Geo):  # true for the middleware's SimpleLazyObject too (it proxies __class__)
        return geo
    return resolve_geo(request)
