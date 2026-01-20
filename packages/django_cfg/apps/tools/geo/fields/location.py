"""
LocationField - Composite field for full location storage.

Stores city_id and provides access to full location hierarchy (city, state, country).
"""

from typing import TYPE_CHECKING, Any, Optional, Tuple

from django.db import models

if TYPE_CHECKING:
    from ..services.schemas import CityDTO, CountryDTO, LocationDTO, StateDTO


class LocationDataDescriptor:
    """
    Descriptor that returns full LocationDTO.

    Usage:
        class Property(models.Model):
            location = LocationField()

        prop.location_data  # LocationDTO with city, state, country
    """

    def __init__(self, field_name: str):
        self.field_name = field_name
        self.cache_attr = f"_location_data_cache_{field_name}"

    def __get__(self, obj: Any, objtype: Any = None) -> Optional["LocationDTO"]:
        if obj is None:
            return self

        cached = getattr(obj, self.cache_attr, None)
        if cached is not None:
            return cached

        city_id = getattr(obj, self.field_name, None)
        if not city_id:
            return None

        from ..services.utils import resolve_location

        result = resolve_location(city_id)
        setattr(obj, self.cache_attr, result)
        return result


class LocationDisplayDescriptor:
    """
    Descriptor that returns formatted location string.

    Usage:
        prop.location_display  # "Seoul, South Korea"
    """

    def __init__(self, field_name: str):
        self.field_name = field_name

    def __get__(self, obj: Any, objtype: Any = None) -> str:
        if obj is None:
            return self

        city_id = getattr(obj, self.field_name, None)
        if not city_id:
            return ""

        from ..services.database import get_geo_db
        from ..services.utils import format_location

        db = get_geo_db()
        city = db.get_city(city_id)
        if not city:
            return ""

        country = db.get_country(city.country_iso2) if city.country_iso2 else None
        return format_location(city=city, country=country)


class LocationCityDescriptor:
    """
    Descriptor that returns CityDTO.

    Usage:
        prop.location_city  # CityDTO
    """

    def __init__(self, field_name: str):
        self.field_name = field_name

    def __get__(self, obj: Any, objtype: Any = None) -> Optional["CityDTO"]:
        if obj is None:
            return self

        city_id = getattr(obj, self.field_name, None)
        if not city_id:
            return None

        from ..services.database import get_geo_db

        return get_geo_db().get_city(city_id)


class LocationCountryDescriptor:
    """
    Descriptor that returns CountryDTO.

    Usage:
        prop.location_country  # CountryDTO
    """

    def __init__(self, field_name: str):
        self.field_name = field_name

    def __get__(self, obj: Any, objtype: Any = None) -> Optional["CountryDTO"]:
        if obj is None:
            return self

        city_id = getattr(obj, self.field_name, None)
        if not city_id:
            return None

        from ..services.database import get_geo_db

        db = get_geo_db()
        city = db.get_city(city_id)
        if not city or not city.country_iso2:
            return None

        return db.get_country(city.country_iso2)


class LocationStateDescriptor:
    """
    Descriptor that returns StateDTO.

    Usage:
        prop.location_state  # StateDTO or None
    """

    def __init__(self, field_name: str):
        self.field_name = field_name

    def __get__(self, obj: Any, objtype: Any = None) -> Optional["StateDTO"]:
        if obj is None:
            return self

        city_id = getattr(obj, self.field_name, None)
        if not city_id:
            return None

        from ..services.database import get_geo_db

        db = get_geo_db()
        city = db.get_city(city_id)
        if not city or not city.state_id:
            return None

        return db.get_state(city.state_id)


class LocationCoordinatesDescriptor:
    """
    Descriptor that returns (latitude, longitude) tuple.

    Usage:
        prop.location_coordinates  # (37.5665, 126.978)
    """

    def __init__(self, field_name: str):
        self.field_name = field_name

    def __get__(self, obj: Any, objtype: Any = None) -> Optional[Tuple[float, float]]:
        if obj is None:
            return self

        city_id = getattr(obj, self.field_name, None)
        if not city_id:
            return None

        from ..services.database import get_geo_db

        city = get_geo_db().get_city(city_id)
        if not city:
            return None

        return city.coordinates


class LocationFlagDescriptor:
    """
    Descriptor that returns country flag emoji.

    Usage:
        prop.location_flag  # "🇰🇷"
    """

    def __init__(self, field_name: str):
        self.field_name = field_name

    def __get__(self, obj: Any, objtype: Any = None) -> str:
        if obj is None:
            return self

        city_id = getattr(obj, self.field_name, None)
        if not city_id:
            return ""

        from ..services.database import get_geo_db

        db = get_geo_db()
        city = db.get_city(city_id)
        if not city or not city.country_iso2:
            return ""

        country = db.get_country(city.country_iso2)
        return country.emoji if country and country.emoji else ""


class LocationField(models.IntegerField):
    """
    Composite location field storing city_id.

    Provides full location hierarchy via descriptors:
    - location_data: Full LocationDTO (city, state, country, coordinates)
    - location_display: Formatted string "Seoul, South Korea"
    - location_city: CityDTO
    - location_state: StateDTO (if available)
    - location_country: CountryDTO
    - location_coordinates: (lat, lon) tuple
    - location_flag: Country emoji flag

    Example:
        class Property(models.Model):
            location = LocationField(null=True, blank=True)

        prop = Property.objects.first()
        print(prop.location)              # 1835848 (city_id)
        print(prop.location_display)      # "Seoul, South Korea"
        print(prop.location_data)         # LocationDTO(city=..., state=..., country=...)
        print(prop.location_city.name)    # "Seoul"
        print(prop.location_country.iso2) # "KR"
        print(prop.location_flag)         # "🇰🇷"
        print(prop.location_coordinates)  # (37.5665, 126.978)
    """

    description = "Location field storing city ID with full location resolution"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("null", True)
        kwargs.setdefault("blank", True)
        kwargs.setdefault("db_index", True)
        super().__init__(*args, **kwargs)

    def contribute_to_class(self, cls: type, name: str) -> None:
        super().contribute_to_class(cls, name)

        # Add descriptors
        setattr(cls, f"{name}_data", LocationDataDescriptor(name))
        setattr(cls, f"{name}_display", LocationDisplayDescriptor(name))
        setattr(cls, f"{name}_city", LocationCityDescriptor(name))
        setattr(cls, f"{name}_state", LocationStateDescriptor(name))
        setattr(cls, f"{name}_country", LocationCountryDescriptor(name))
        setattr(cls, f"{name}_coordinates", LocationCoordinatesDescriptor(name))
        setattr(cls, f"{name}_flag", LocationFlagDescriptor(name))

    def deconstruct(self) -> tuple:
        name, path, args, kwargs = super().deconstruct()
        # Remove defaults we set
        if kwargs.get("null") is True:
            del kwargs["null"]
        if kwargs.get("blank") is True:
            del kwargs["blank"]
        if kwargs.get("db_index") is True:
            del kwargs["db_index"]
        return name, path, args, kwargs

    def formfield(self, **kwargs: Any) -> Any:
        from ..widgets.location_widget import LocationFieldWidget

        defaults = {
            "widget": LocationFieldWidget(
                show_map=True,
                map_height="160px",
            )
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)


__all__ = ["LocationField"]
