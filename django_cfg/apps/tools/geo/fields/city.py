"""
CityField - IntegerField for storing city IDs.

Auto-creates properties:
- {field}_data: CityDTO object
- {field}_display: Formatted display name
- {field}_country: Country ISO2 code
- {field}_coordinates: (lat, lng) tuple
"""

from typing import Any, Optional, Tuple

from django.core.exceptions import ValidationError
from django.db import models

from ..services.schemas import CityDTO


class CityDataDescriptor:
    """
    Descriptor for {field}_data property.

    Returns full CityDTO object.
    """

    def __init__(self, field_name: str):
        self.field_name = field_name

    def __get__(self, obj: Any, objtype: Any = None) -> Optional[CityDTO]:
        if obj is None:
            return None

        city_id = getattr(obj, self.field_name, None)
        if not city_id:
            return None

        from ..services.database import get_geo_db

        return get_geo_db().get_city(city_id)


class CityDisplayDescriptor:
    """
    Descriptor for {field}_display property.

    Returns formatted display name (e.g., "Seoul, 11, KR").
    """

    def __init__(self, field_name: str):
        self.field_name = field_name

    def __get__(self, obj: Any, objtype: Any = None) -> Optional[str]:
        if obj is None:
            return None

        city_id = getattr(obj, self.field_name, None)
        if not city_id:
            return None

        from ..services.database import get_geo_db

        city = get_geo_db().get_city(city_id)
        return city.display_name if city else None


class CityCountryDescriptor:
    """
    Descriptor for {field}_country property.

    Returns country ISO2 code.
    """

    def __init__(self, field_name: str):
        self.field_name = field_name

    def __get__(self, obj: Any, objtype: Any = None) -> Optional[str]:
        if obj is None:
            return None

        city_id = getattr(obj, self.field_name, None)
        if not city_id:
            return None

        from ..services.database import get_geo_db

        city = get_geo_db().get_city(city_id)
        return city.country_iso2 if city else None


class CityCoordinatesDescriptor:
    """
    Descriptor for {field}_coordinates property.

    Returns (latitude, longitude) tuple.
    """

    def __init__(self, field_name: str):
        self.field_name = field_name

    def __get__(self, obj: Any, objtype: Any = None) -> Optional[Tuple[float, float]]:
        if obj is None:
            return None

        city_id = getattr(obj, self.field_name, None)
        if not city_id:
            return None

        from ..services.database import get_geo_db

        city = get_geo_db().get_city(city_id)
        return city.coordinates if city else None


class CityField(models.IntegerField):
    """
    Field for storing city IDs.

    Auto-creates properties:
    - {field}_data: CityDTO object with full city data
    - {field}_display: Formatted display name (e.g., "Seoul, 11, KR")
    - {field}_country: Country ISO2 code (e.g., "KR")
    - {field}_coordinates: (latitude, longitude) tuple

    Usage:
        class Property(models.Model):
            city = CityField()

        # Access:
        property.city              # 12345 (city ID)
        property.city_data         # CityDTO(id=12345, name="Seoul", ...)
        property.city_display      # "Seoul, 11, KR"
        property.city_country      # "KR"
        property.city_coordinates  # (37.5665, 126.978)
    """

    def __init__(self, *args: Any, **kwargs: Any):
        kwargs.setdefault("null", True)
        kwargs.setdefault("blank", True)
        kwargs.setdefault("db_index", True)
        super().__init__(*args, **kwargs)

    def contribute_to_class(self, cls: Any, name: str, private_only: bool = False) -> None:
        super().contribute_to_class(cls, name, private_only)

        # Add computed properties
        setattr(cls, f"{name}_data", CityDataDescriptor(name))
        setattr(cls, f"{name}_display", CityDisplayDescriptor(name))
        setattr(cls, f"{name}_country", CityCountryDescriptor(name))
        setattr(cls, f"{name}_coordinates", CityCoordinatesDescriptor(name))

    def validate(self, value: Any, model_instance: Any) -> None:
        super().validate(value, model_instance)

        if value:
            from ..services.database import get_geo_db

            city = get_geo_db().get_city(int(value))
            if not city:
                raise ValidationError(f"Invalid city ID: {value}")

    def deconstruct(self) -> tuple:
        name, path, args, kwargs = super().deconstruct()
        # Remove defaults that match our custom defaults
        if kwargs.get("null") is True:
            del kwargs["null"]
        if kwargs.get("blank") is True:
            del kwargs["blank"]
        if kwargs.get("db_index") is True:
            del kwargs["db_index"]
        return name, path, args, kwargs


__all__ = ["CityField"]
