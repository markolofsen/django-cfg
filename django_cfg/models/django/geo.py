"""
Geo configuration model.
"""

from typing import List

from pydantic import BaseModel, Field, field_validator


class GeoConfig(BaseModel):
    """
    Geo app configuration for geographic data (countries, states, cities).

    Uses PostgreSQL with Django ORM. Data from dr5hn dataset
    (250+ countries, 5000+ states, 150,000+ cities).

    Example:
        ```python
        from django_cfg import DjangoConfig, GeoConfig

        class MyConfig(DjangoConfig):
            # Whole dataset.
            geo = GeoConfig()

            # Only the markets this project serves — a few hundred rows
            # instead of ~150,000 cities.
            geo = GeoConfig(countries=["BB", "BS", "KY", "LC", "TC"])
        ```
    """

    enabled: bool = Field(
        default=True,
        description="Enable geo app (auto-adds to INSTALLED_APPS)"
    )

    database: str = Field(
        default="default",
        description=(
            "DATABASES alias where cfg_geo tables live. Set to a non-default "
            "alias if your project's domain models (vehicles, listings, etc.) "
            "live in a secondary DB and you want JOINs or co-located queries. "
            "Non-default values are auto-registered in DATABASE_ROUTING_RULES."
        )
    )

    countries: List[str] = Field(
        default_factory=list,
        description=(
            "ISO2 codes to populate, e.g. ['BB', 'BS', 'KY']. Empty means the "
            "whole dataset (250 countries, 5k states, 150k cities). Most "
            "projects serve a handful of markets and have no use for the rest: "
            "restricting the load keeps the tables small, the import fast, and "
            "reverse-geocoding confined to real coverage. States and cities "
            "are filtered to the selected countries automatically."
        ),
    )

    auto_populate: bool = Field(
        default=True,
        description="Auto-populate geo data on startup if empty"
    )

    @field_validator("countries")
    @classmethod
    def _validate_countries(cls, value: List[str]) -> List[str]:
        """Normalize to upper-case ISO2 and reject anything malformed.

        Failing here beats silently importing nothing: a typo like 'Barbados'
        or 'bb ' would otherwise produce an empty database that looks like a
        download problem.
        """
        normalized: List[str] = []
        for raw in value:
            code = str(raw).strip().upper()
            if len(code) != 2 or not code.isalpha():
                raise ValueError(
                    f"GeoConfig.countries expects 2-letter ISO2 codes; got {raw!r}. "
                    "Use 'BB' for Barbados, not a country name."
                )
            if code not in normalized:
                normalized.append(code)
        return normalized

    use_postgis: bool = Field(
        default=False,
        description="Use PostGIS for spatial queries (requires PostGIS extension)"
    )


__all__ = ["GeoConfig"]
