"""What `request.geo` may hold. Country by default; region, city, ASN and bot signals are opt-in.

A field above `level` stays empty even when Cloudflare sends it, so enabling a zone transform never widens what an
app collects. Edge trust (who may send the headers) is `edge` config, not this one.

Env: every field as `VISITOR_GEO__<FIELD>` (e.g. `VISITOR_GEO__LEVEL=city`). (`geo` is the country/city reference app, `models/django/geo.py`.)
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

GeoLevel = Literal["off", "country", "region", "city"]
LEVEL_RANK = {"off": 0, "country": 1, "region": 2, "city": 3}


class GeoOverride(BaseModel):
    """Fixed geography for local development (debug only) and tests."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    country: str = ""
    region: str = ""
    region_code: str = ""
    city: str = ""
    timezone: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    asn: Optional[int] = None


class VisitorGeoConfig(BaseSettings):
    """Visitor geography from the edge (Cloudflare) or an optional local database."""

    model_config = SettingsConfigDict(
        env_prefix="VISITOR_GEO__",
        case_sensitive=False,
        validate_assignment=True,
        validate_default=True,
        extra="forbid",
    )

    level: GeoLevel = Field(
        default="country",
        description=(
            "off | country | region | city. Region and city need Cloudflare's 'Add visitor location headers' "
            "Managed Transform on the zone. City and coordinates are personal data: opt in deliberately."
        ),
    )
    asn: bool = Field(
        default=False,
        description="Read the network number from `asn_header` (a Cloudflare Transform Rule: to_string(ip.src.asnum))",
    )
    asn_header: str = Field(default="X-Edge-ASN", description="Header the ASN Transform Rule writes")
    bot: bool = Field(
        default=False,
        description="Read cf-bot-score / cf-verified-bot (Cloudflare Bot Management, Enterprise)",
    )
    coords_precision: int = Field(
        default=1, ge=0, le=2,
        description="Decimals kept on latitude/longitude: 1 = about 11 km, 2 = about 1 km",
    )
    fallback: Literal["none", "geoip2"] = Field(
        default="none",
        description="Lookup when edge headers are absent or untrusted. geoip2 needs `django-cfg[geoip]` and a .mmdb",
    )
    geoip_path: Optional[str] = Field(
        default=None,
        description="Directory or file of the GeoLite2/DB-IP .mmdb for fallback='geoip2'",
    )
    dev_override: Optional[GeoOverride] = Field(
        default=None,
        description="Geography for untrusted requests while debug=True (e.g. localhost renders as GE)",
    )

    @field_validator("asn_header")
    @classmethod
    def _header(cls, value: str) -> str:
        if not value or any(c in value for c in " :\r\n"):
            raise ValueError("visitor_geo.asn_header must be a plain header name")
        return value

    def allows(self, level: str) -> bool:
        return LEVEL_RANK[self.level] >= LEVEL_RANK[level]
