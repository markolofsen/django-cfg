# Compatibility shim — classes moved to geo/ subpackage.
# Will be removed in a future release.
from .geo import CityDisplay, CoordinatesDisplay, CountryDisplay, LocationDisplay

__all__ = ["CountryDisplay", "CityDisplay", "LocationDisplay", "CoordinatesDisplay"]
