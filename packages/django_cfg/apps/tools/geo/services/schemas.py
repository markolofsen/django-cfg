"""
Pydantic DTOs for geographic data.

Data transfer objects for type-safe geographic data handling.
"""

from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, computed_field


class CountryDTO(BaseModel):
    """Country data transfer object."""

    model_config = ConfigDict(from_attributes=True, frozen=True)

    id: int
    name: str
    iso2: str
    iso3: Optional[str] = None
    numeric_code: Optional[str] = None
    phonecode: Optional[str] = None
    capital: Optional[str] = None
    currency: Optional[str] = None
    currency_name: Optional[str] = None
    currency_symbol: Optional[str] = None
    tld: Optional[str] = None
    native: Optional[str] = None
    region: Optional[str] = None
    subregion: Optional[str] = None
    nationality: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    emoji: Optional[str] = None
    timezones: Optional[List[Any]] = None

    @computed_field
    @property
    def display_name(self) -> str:
        """Format: 'South Korea (KR)'"""
        return f"{self.name} ({self.iso2})" if self.iso2 else self.name

    @computed_field
    @property
    def coordinates(self) -> Optional[tuple[float, float]]:
        """Return (latitude, longitude) tuple or None."""
        if self.latitude is not None and self.longitude is not None:
            return (self.latitude, self.longitude)
        return None


class StateDTO(BaseModel):
    """State/Province data transfer object."""

    model_config = ConfigDict(from_attributes=True, frozen=True)

    id: int
    name: str
    country_id: int
    iso2: Optional[str] = None
    type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    # Populated from relation
    country_iso2: Optional[str] = None

    @computed_field
    @property
    def display_name(self) -> str:
        """Format: 'California, US'"""
        if self.country_iso2:
            return f"{self.name}, {self.country_iso2}"
        return self.name


class CityDTO(BaseModel):
    """City data transfer object."""

    model_config = ConfigDict(from_attributes=True, frozen=True)

    id: int
    name: str
    state_id: Optional[int] = None
    country_id: int
    latitude: float
    longitude: float

    # Populated from relations
    state_iso2: Optional[str] = None
    country_iso2: Optional[str] = None

    @computed_field
    @property
    def display_name(self) -> str:
        """Format: 'Seoul, 11, KR' or 'Singapore, SG'"""
        parts = [self.name]
        if self.state_iso2:
            parts.append(self.state_iso2)
        if self.country_iso2:
            parts.append(self.country_iso2)
        return ", ".join(parts)

    @computed_field
    @property
    def coordinates(self) -> tuple[float, float]:
        """Return (latitude, longitude) tuple."""
        return (self.latitude, self.longitude)


class LocationDTO(BaseModel):
    """Composite location with all resolved data."""

    model_config = ConfigDict(from_attributes=True, frozen=True)

    city: Optional[CityDTO] = None
    state: Optional[StateDTO] = None
    country: Optional[CountryDTO] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @computed_field
    @property
    def display_name(self) -> str:
        """Format: 'Seoul, Seoul, South Korea'"""
        parts = []
        if self.city:
            parts.append(self.city.name)
        if self.state:
            parts.append(self.state.name)
        if self.country:
            parts.append(self.country.name)
        return ", ".join(parts) if parts else "Unknown"

    @computed_field
    @property
    def coordinates(self) -> Optional[tuple[float, float]]:
        """Return (latitude, longitude) tuple or None."""
        if self.latitude is not None and self.longitude is not None:
            return (self.latitude, self.longitude)
        return None


class NearbyResult(BaseModel):
    """Result from proximity search."""

    model_config = ConfigDict(frozen=True)

    city: CityDTO
    distance_km: float

    @computed_field
    @property
    def display_name(self) -> str:
        """Format: 'Seoul, 11, KR (5.2 km)'"""
        return f"{self.city.display_name} ({self.distance_km:.1f} km)"


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                         GEOCODING DTOs                                    ║
# ╚══════════════════════════════════════════════════════════════════════════╝


class AddressComponents(BaseModel):
    """Parsed address components from geocoding."""

    model_config = ConfigDict(frozen=True)

    house_number: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    postal_code: Optional[str] = None


class GeocodingResult(BaseModel):
    """Result from geocoding an address to coordinates."""

    model_config = ConfigDict(frozen=True)

    latitude: float
    longitude: float
    display_name: str
    address: AddressComponents
    confidence: float = 1.0  # 0-1 score
    source: str = "nominatim"  # 'nominatim', 'photon', 'local', 'cache'

    @computed_field
    @property
    def coordinates(self) -> tuple[float, float]:
        """Return (latitude, longitude) tuple."""
        return (self.latitude, self.longitude)


class ReverseGeocodingResult(BaseModel):
    """Result from reverse geocoding coordinates to address."""

    model_config = ConfigDict(frozen=True)

    display_name: str
    address: AddressComponents
    city_id: Optional[int] = None  # Matched local city if found
    city_name: Optional[str] = None
    distance_to_city_center: Optional[float] = None  # km
    source: str = "nominatim"


class AutocompleteResult(BaseModel):
    """Autocomplete suggestion for address search."""

    model_config = ConfigDict(frozen=True)

    text: str
    place_id: str
    latitude: float
    longitude: float
    type: str = "address"  # 'city', 'address', 'poi'


__all__ = [
    "CountryDTO",
    "StateDTO",
    "CityDTO",
    "LocationDTO",
    "NearbyResult",
    # Geocoding
    "AddressComponents",
    "GeocodingResult",
    "ReverseGeocodingResult",
    "AutocompleteResult",
]
