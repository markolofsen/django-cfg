"""
Geographic data models.

Country, State, City models using PostgreSQL with Django ORM.
Data sourced from dr5hn/countries-states-cities-database.
"""

from django.db import models


class Country(models.Model):
    """
    Country with ISO codes and metadata.

    Fields include ISO2/ISO3 codes, currency info, timezone data,
    coordinates, and flag emoji.
    """

    id = models.IntegerField(primary_key=True)  # dr5hn ID
    name = models.CharField(max_length=100, db_index=True)
    iso2 = models.CharField(max_length=2, unique=True, db_index=True)
    iso3 = models.CharField(max_length=3, null=True, blank=True)
    numeric_code = models.CharField(max_length=3, null=True, blank=True)
    phonecode = models.CharField(max_length=20, null=True, blank=True)
    capital = models.CharField(max_length=100, null=True, blank=True)
    currency = models.CharField(max_length=3, null=True, blank=True)
    currency_name = models.CharField(max_length=100, null=True, blank=True)
    currency_symbol = models.CharField(max_length=10, null=True, blank=True)
    tld = models.CharField(max_length=10, null=True, blank=True)
    native = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=50, null=True, blank=True)
    subregion = models.CharField(max_length=100, null=True, blank=True)
    nationality = models.CharField(max_length=100, null=True, blank=True)
    timezones = models.JSONField(null=True, blank=True)
    translations = models.JSONField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    emoji = models.CharField(max_length=10, null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "cfg_geo_country"
        verbose_name = "Country"
        verbose_name_plural = "Countries"
        ordering = ["name"]

    def __str__(self) -> str:
        if self.emoji:
            return f"{self.emoji} {self.name}"
        return self.name

    @property
    def display_name(self) -> str:
        """Format: 'South Korea (KR)'"""
        return f"{self.name} ({self.iso2})" if self.iso2 else self.name


class State(models.Model):
    """
    State/Province/Region within a country.

    Includes state/province code, type, and coordinates.
    """

    id = models.IntegerField(primary_key=True)  # dr5hn ID
    name = models.CharField(max_length=200, db_index=True)
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="states"
    )
    iso2 = models.CharField(max_length=10, null=True, blank=True)
    type = models.CharField(max_length=50, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "cfg_geo_state"
        verbose_name = "State"
        verbose_name_plural = "States"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["country", "name"]),
        ]

    def __str__(self) -> str:
        return f"{self.name}, {self.country.iso2}"

    @property
    def display_name(self) -> str:
        """Format: 'California, US'"""
        return f"{self.name}, {self.country.iso2}"


class City(models.Model):
    """
    City with coordinates.

    Linked to Country and optionally to State.
    Includes latitude/longitude for proximity searches.
    """

    id = models.IntegerField(primary_key=True)  # dr5hn ID
    name = models.CharField(max_length=200, db_index=True)
    state = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        related_name="cities",
        null=True,
        blank=True
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="cities"
    )
    latitude = models.FloatField(db_index=True)
    longitude = models.FloatField(db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "cfg_geo_city"
        verbose_name = "City"
        verbose_name_plural = "Cities"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["country", "name"]),
            models.Index(fields=["state", "name"]),
            models.Index(fields=["latitude", "longitude"]),
        ]

    def __str__(self) -> str:
        if self.state:
            return f"{self.name}, {self.state.iso2 or self.state.name}, {self.country.iso2}"
        return f"{self.name}, {self.country.iso2}"

    @property
    def display_name(self) -> str:
        """Format: 'Seoul, 11, KR' or 'Singapore, SG'"""
        parts = [self.name]
        if self.state and self.state.iso2:
            parts.append(self.state.iso2)
        parts.append(self.country.iso2)
        return ", ".join(parts)

    @property
    def coordinates(self) -> tuple[float, float]:
        """Return (latitude, longitude) tuple."""
        return (self.latitude, self.longitude)


__all__ = ["Country", "State", "City"]
