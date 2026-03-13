"""OG image presets — typed, frozen visual configurations.

Usage::

    from django_cfg.modules.django_ogimage.presets import DARK_BLUE, get_preset, build_preset
    from django_cfg.modules.django_ogimage import get_or_create_og_url

    # By object
    url = get_or_create_og_url(DARK_BLUE.to_params(title="Hello", description="World"))

    # By name (string)
    url = get_or_create_og_url(get_preset("dark_blue").to_params(title="Hello"))

    # Custom preset
    MY_BRAND = build_preset("brand", "#0f0c29", "#302b63", "#e91e63")
    url = get_or_create_og_url(MY_BRAND.to_params(title="My Brand Page"))
"""
from ._base import OGImagePreset
from .dark import DARK, DARK_BLUE, DARK_GREEN, DARK_PURPLE, DARK_ROSE
from .light import LIGHT, LIGHT_GRAY, LIGHT_GREEN, LIGHT_WARM
from .utils import build_preset

ALL: dict[str, OGImagePreset] = {
    p.name: p
    for p in [
        DARK, DARK_BLUE, DARK_PURPLE, DARK_GREEN, DARK_ROSE,
        LIGHT, LIGHT_GRAY, LIGHT_WARM, LIGHT_GREEN,
    ]
}


def get_preset(name: str) -> OGImagePreset:
    """Return a built-in preset by its slug name.

    Args:
        name: Preset slug, e.g. ``"dark_blue"``, ``"light_warm"``.

    Raises:
        ValueError: If the name is not a registered preset.

    Example::

        preset = get_preset("dark_blue")
        url = get_or_create_og_url(preset.to_params(title="Hello"))
    """
    try:
        return ALL[name]
    except KeyError:
        available = ", ".join(sorted(ALL))
        raise ValueError(f"Unknown preset: {name!r}. Available: {available}")


__all__ = [
    # base class
    "OGImagePreset",
    # registry
    "ALL",
    "get_preset",
    # dark presets
    "DARK",
    "DARK_BLUE",
    "DARK_PURPLE",
    "DARK_GREEN",
    "DARK_ROSE",
    # light presets
    "LIGHT",
    "LIGHT_GRAY",
    "LIGHT_WARM",
    "LIGHT_GREEN",
    # helpers
    "build_preset",
]
