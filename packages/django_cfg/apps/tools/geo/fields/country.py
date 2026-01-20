"""
CountryField - CharField for storing ISO2 country codes.

Auto-creates display property: {field}_display
"""

from typing import Any, Optional

from django.core.exceptions import ValidationError
from django.db import models


class CountryDisplayDescriptor:
    """
    Descriptor for {field}_display property.

    Returns country display name (e.g., "South Korea (KR)").
    """

    def __init__(self, field_name: str):
        self.field_name = field_name

    def __get__(self, obj: Any, objtype: Any = None) -> Optional[str]:
        if obj is None:
            return None

        code = getattr(obj, self.field_name, None)
        if not code:
            return None

        from ..services.database import get_geo_db

        country = get_geo_db().get_country(code)
        return country.display_name if country else code


class CountryEmojiDescriptor:
    """
    Descriptor for {field}_emoji property.

    Returns country flag emoji (e.g., "🇰🇷").
    """

    def __init__(self, field_name: str):
        self.field_name = field_name

    def __get__(self, obj: Any, objtype: Any = None) -> Optional[str]:
        if obj is None:
            return None

        code = getattr(obj, self.field_name, None)
        if not code:
            return None

        from ..services.database import get_geo_db

        country = get_geo_db().get_country(code)
        return country.emoji if country else None


class CountryField(models.CharField):
    """
    Field for storing country ISO2 codes.

    Auto-creates properties:
    - {field}_display: Formatted country name (e.g., "South Korea (KR)")
    - {field}_emoji: Country flag emoji (e.g., "🇰🇷")

    Usage:
        class Property(models.Model):
            country = CountryField()

        # Access:
        property.country           # "KR"
        property.country_display   # "South Korea (KR)"
        property.country_emoji     # "🇰🇷"
    """

    def __init__(self, *args: Any, **kwargs: Any):
        kwargs.setdefault("max_length", 2)
        kwargs.setdefault("null", True)
        kwargs.setdefault("blank", True)
        kwargs.setdefault("db_index", True)
        super().__init__(*args, **kwargs)

    def contribute_to_class(self, cls: Any, name: str, private_only: bool = False) -> None:
        super().contribute_to_class(cls, name, private_only)

        # Add display property
        setattr(cls, f"{name}_display", CountryDisplayDescriptor(name))

        # Add emoji property
        setattr(cls, f"{name}_emoji", CountryEmojiDescriptor(name))

    def validate(self, value: Any, model_instance: Any) -> None:
        super().validate(value, model_instance)

        if value:
            from ..services.database import get_geo_db

            country = get_geo_db().get_country(value)
            if not country:
                raise ValidationError(f"Invalid country code: {value}")

    def get_prep_value(self, value: Any) -> Optional[str]:
        if value is None:
            return None
        return str(value).upper()[:2]

    def deconstruct(self) -> tuple:
        name, path, args, kwargs = super().deconstruct()
        # Remove defaults that match our custom defaults
        if kwargs.get("max_length") == 2:
            del kwargs["max_length"]
        if kwargs.get("null") is True:
            del kwargs["null"]
        if kwargs.get("blank") is True:
            del kwargs["blank"]
        if kwargs.get("db_index") is True:
            del kwargs["db_index"]
        return name, path, args, kwargs


__all__ = ["CountryField"]
