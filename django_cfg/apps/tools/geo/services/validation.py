"""
Geocode result validation.

Sanity-checks a geocoded point against the reference geography the package
already ships (`cfg_geo_city` rows for the requested country/state).

The country filter Nominatim offers is not a defence: a wrong result inside a
5,000 km-wide country is still inside the country. The check here is
*nearest-reference-city*, not distance-from-centroid — a centroid check rejects
the Canary Islands against ES, Hawaii against US, and every archipelago.

When the reference set is too thin to bound anything the validator ABSTAINS.
dr5hn genuinely holds 0 cities for several small territories; a missing
reference is not evidence of a bad result.
"""

from __future__ import annotations

import logging
import math
from enum import Enum
from typing import Optional, Sequence

logger = logging.getLogger(__name__)

# Max accepted distance from the nearest reference city, in km.
#
# Measured against the shipped dr5hn data (data/cities.json), the worst
# legitimate point is interior Alaska at 46 km from its nearest US row; the
# Canaries sit 9 km from a Spanish row and Hawaii 17 km. The closest of the
# four known-bad results is 236 km from Bali. 150 km sits between those bands
# with room on both sides.
DEFAULT_MAX_DISTANCE_KM = 150.0

# Below this many reference rows we cannot bound anything — abstain.
MIN_REFERENCE_CITIES = 1

EARTH_RADIUS_KM = 6371.0088


class ValidationStatus(str, Enum):
    """Outcome of validating a geocoded point against reference geography."""

    VALID = "valid"          # point sits near known reference geography
    SUSPECT = "suspect"      # inside the country but far from anything known
    INVALID = "invalid"      # coordinates unusable (out of domain, NaN, null island)
    UNVERIFIED = "unverified"  # no usable reference data — abstained


#: Statuses a caller should treat as "do not trust this point".
FLAGGED_STATUSES = frozenset({ValidationStatus.SUSPECT, ValidationStatus.INVALID})


def is_finite_number(value) -> bool:
    """True for a real, finite float/int (rejects None, NaN, inf, str)."""
    if value is None or isinstance(value, bool):
        return False
    if not isinstance(value, (int, float)):
        return False
    return math.isfinite(float(value))


def coordinates_in_domain(latitude, longitude) -> bool:
    """True if the pair is finite and within ±90 / ±180."""
    if not is_finite_number(latitude) or not is_finite_number(longitude):
        return False
    return -90.0 <= float(latitude) <= 90.0 and -180.0 <= float(longitude) <= 180.0


def is_null_island(latitude, longitude, tolerance: float = 1e-7) -> bool:
    """True for 0,0 — the classic 'coordinates were never set' sentinel."""
    if not is_finite_number(latitude) or not is_finite_number(longitude):
        return False
    return abs(float(latitude)) < tolerance and abs(float(longitude)) < tolerance


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance in km. Handles antimeridian correctly by construction."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    d_lat = p2 - p1
    d_lng = math.radians(lng2 - lng1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(d_lng / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(min(1.0, math.sqrt(a)))


class GeocodeValidation:
    """Immutable verdict for one geocoded point."""

    __slots__ = ("status", "reason", "distance_km", "reference")

    def __init__(
        self,
        status: ValidationStatus,
        reason: str = "",
        distance_km: Optional[float] = None,
        reference: Optional[str] = None,
    ):
        self.status = status
        self.reason = reason
        self.distance_km = distance_km
        self.reference = reference

    @property
    def is_flagged(self) -> bool:
        """True when the caller should not trust the coordinates."""
        return self.status in FLAGGED_STATUSES

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return (
            f"GeocodeValidation(status={self.status.value!r}, reason={self.reason!r}, "
            f"distance_km={self.distance_km!r}, reference={self.reference!r})"
        )


def _nearest_reference(
    latitude: float,
    longitude: float,
    references: Sequence[tuple[float, float]],
) -> Optional[float]:
    """Distance in km to the closest usable reference point, or None if none are usable."""
    best: Optional[float] = None
    for ref_lat, ref_lng in references:
        if not coordinates_in_domain(ref_lat, ref_lng):
            continue
        d = haversine_km(latitude, longitude, float(ref_lat), float(ref_lng))
        if best is None or d < best:
            best = d
    return best


class GeocodeValidator:
    """
    Validates a geocoded point against `cfg_geo_city` reference rows.

    Reference rows are fetched via a pluggable ``reference_loader`` so the
    check is unit-testable with no database and no network.
    """

    def __init__(
        self,
        max_distance_km: float = DEFAULT_MAX_DISTANCE_KM,
        min_reference_cities: int = MIN_REFERENCE_CITIES,
        reference_loader=None,
    ):
        self.max_distance_km = max_distance_km
        self.min_reference_cities = min_reference_cities
        self._reference_loader = reference_loader or _default_reference_loader

    def validate(
        self,
        latitude,
        longitude,
        country_code: Optional[str] = None,
        state_name: Optional[str] = None,
    ) -> GeocodeValidation:
        """
        Check a point. Never raises — bad input becomes an INVALID verdict.

        Prefers state-level reference rows (the level at which Indonesia and
        Spain actually fail) and falls back to country level.
        """
        # 1. Domain checks — cheap, catch corruption before touching the DB.
        if not is_finite_number(latitude) or not is_finite_number(longitude):
            return GeocodeValidation(ValidationStatus.INVALID, "non-numeric or NaN coordinates")

        latitude, longitude = float(latitude), float(longitude)

        if not coordinates_in_domain(latitude, longitude):
            return GeocodeValidation(ValidationStatus.INVALID, "coordinates outside ±90/±180")

        if is_null_island(latitude, longitude):
            return GeocodeValidation(ValidationStatus.INVALID, "null island (0,0)")

        # 2. Reference check. No country to check against -> nothing to say.
        if not country_code:
            return GeocodeValidation(ValidationStatus.UNVERIFIED, "no country code supplied")

        try:
            references, scope = self._load_references(country_code, state_name)
        except Exception as e:  # reference lookup must never break geocoding
            logger.warning(f"Geocode validation reference lookup failed: {e}")
            return GeocodeValidation(ValidationStatus.UNVERIFIED, "reference lookup failed")

        usable = [r for r in references if coordinates_in_domain(r[0], r[1])]
        if len(usable) < self.min_reference_cities:
            return GeocodeValidation(
                ValidationStatus.UNVERIFIED,
                f"no usable reference rows for {scope}",
                reference=scope,
            )

        # Nearest reference, not centroid: archipelagos and exclaves must pass.
        nearest = _nearest_reference(latitude, longitude, usable)
        if nearest is None:
            return GeocodeValidation(
                ValidationStatus.UNVERIFIED, f"no usable reference rows for {scope}", reference=scope
            )

        if nearest <= self.max_distance_km:
            return GeocodeValidation(
                ValidationStatus.VALID, "near known reference geography", nearest, scope
            )

        return GeocodeValidation(
            ValidationStatus.SUSPECT,
            f"{nearest:.0f} km from nearest known place in {scope}",
            nearest,
            scope,
        )

    def _load_references(
        self,
        country_code: str,
        state_name: Optional[str],
    ) -> tuple[Sequence[tuple[float, float]], str]:
        """Return (reference points, human-readable scope). State first, country as fallback."""
        if state_name:
            rows = self._reference_loader(country_code, state_name)
            if rows and len(rows) >= self.min_reference_cities:
                return rows, f"{state_name}, {country_code.upper()}"

        rows = self._reference_loader(country_code, None)
        return rows, country_code.upper()


def _default_reference_loader(
    country_code: str,
    state_name: Optional[str],
) -> Sequence[tuple[float, float]]:
    """Load city coordinates from `cfg_geo_city` for a country, optionally narrowed to a state."""
    from ..models import City

    qs = City.objects.filter(is_active=True, country__iso2=country_code.upper())
    if state_name:
        qs = qs.filter(state__name__iexact=state_name)
    return list(qs.values_list("latitude", "longitude"))


_validator: Optional[GeocodeValidator] = None


def get_geocode_validator() -> GeocodeValidator:
    """Shared GeocodeValidator instance."""
    global _validator
    if _validator is None:
        _validator = GeocodeValidator()
    return _validator


__all__ = [
    "ValidationStatus",
    "GeocodeValidation",
    "GeocodeValidator",
    "get_geocode_validator",
    "coordinates_in_domain",
    "is_null_island",
    "is_finite_number",
    "haversine_km",
    "FLAGGED_STATUSES",
    "DEFAULT_MAX_DISTANCE_KM",
]
