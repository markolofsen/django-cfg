"""Location display utility — full hierarchy alias for CityDisplay."""
from __future__ import annotations

from typing import Any

from django.utils.safestring import SafeString

from .._types import CityDisplayConfig
from .city import CityDisplay


class LocationDisplay:
    """
    Display full location with city, state, country.

    Alias for CityDisplay with all components enabled by default.
    """

    @classmethod
    def from_field(cls, obj: Any, field_name: str, config: CityDisplayConfig | None = None) -> SafeString:
        """Render location field with full hierarchy. Same config as CityDisplay."""
        cfg: CityDisplayConfig = dict(config) if config else {}  # type: ignore[arg-type]
        cfg.setdefault("show_flag", True)
        cfg.setdefault("show_state", True)
        cfg.setdefault("show_country", True)
        return CityDisplay.from_field(obj, field_name, cfg)
